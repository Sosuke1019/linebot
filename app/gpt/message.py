from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .constants import Role

@dataclass
class Message:
    role: Role
    content: str

    # -> Dict[str, str] はこのメソッドが辞書型を返すことを示す
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role.value, "content": self.content}
    
    @classmethod
    # 辞書型を受け取ってMessageオブジェクトを精製するためのメソッド
    def from_dict(cls, message: Dict[str,str]) -> Message:
        return cls(role=Role(message["role"]), content=message["content"])