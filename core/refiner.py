import json
import os
from dataclasses import dataclass, field
from typing import Literal

from groq import Groq

ChangeType = Literal["removed", "clarified", "restructured", "added"]

SYSTEM_PROMPT = """You are a Prompt Refinement Engine. Your sole job is to take a raw, noisy user prompt and return a clean, refined version suitable for sending to a production LLM.

WHAT YOU DO:
1. Remove filler words, redundancy, typos, informal language ("u", "wanna", "kinda", "i was thinking")
2. Remove unnecessary context, backstory, or meta-commentary ("not sure if this is right but...", "I just had this idea...")
3. Eliminate ambiguity — replace vague terms with specific, actionable ones
4. Make implicit assumptions explicit (add missing context if required)
5. Structure the prompt properly: clear instruction → context → constraints → output format (if applicable)
6. Preserve the original INTENT faithfully — don't change what the user wants, just how it's expressed

OUTPUT FORMAT (strict JSON, nothing else):
{
  "refined_prompt": "<the clean, refined prompt>",
  "changes": [
    { "type": "removed" | "clarified" | "restructured" | "added", "description": "<brief explanation of change>" }
  ],
  "quality_score": <integer 1-10, how good the original prompt was>,
  "intent_summary": "<1 sentence: what the user actually wants>"
}

Return ONLY valid JSON. No explanation, no markdown, no preamble."""

# Available free Groq models (update as Groq adds more)
GROQ_MODELS = [
    "llama-3.3-70b-versatile",   # best quality, still very fast
    "llama-3.1-8b-instant",      # fastest, lighter
    "mixtral-8x7b-32768",        # good for structured output
    "gemma2-9b-it",              # Google Gemma 2
]


@dataclass
class Change:
    type: ChangeType
    description: str


@dataclass
class RefinementResult:
    refined_prompt: str
    intent_summary: str
    quality_score: int
    changes: list[Change] = field(default_factory=list)
    raw_input: str = ""

    @classmethod
    def from_dict(cls, data: dict, raw_input: str = "") -> "RefinementResult":
        changes = [Change(**c) for c in data.get("changes", [])]
        return cls(
            refined_prompt=data["refined_prompt"],
            intent_summary=data["intent_summary"],
            quality_score=int(data["quality_score"]),
            changes=changes,
            raw_input=raw_input,
        )


class PromptRefiner:
    def __init__(self, api_key: str | None = None, model: str = "llama-3.3-70b-versatile"):
        key = api_key or os.getenv("GROQ_API_KEY", "")
        if not key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY or pass api_key=.")
        self.client = Groq(api_key=key)
        self.model = model

    def refine(self, raw_prompt: str) -> RefinementResult:
        """Send a raw prompt to Groq and get back a structured refinement result."""
        if not raw_prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_prompt},
            ],
            response_format={"type": "json_object"},  # Groq supports forced JSON mode
        )

        raw_text = response.choices[0].message.content
        data = json.loads(raw_text)
        return RefinementResult.from_dict(data, raw_input=raw_prompt)
