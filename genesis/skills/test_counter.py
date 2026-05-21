import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from genesis.core.base import Tool


class TestCounterTool:
    @property
    def name(self):
        return "test_counter"
        
    @property
    def description(self):
        return "简单的计数器工具"
        
    @property
    def parameters(self):
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "操作: increment, reset, get"}
            },
            "required": ["action"]
        }
        
    async def execute(self, action: str):
        if not hasattr(self, '_counter'):
            self._counter = 0
            
        if action == "increment":
            self._counter += 1
            return f"计数器增加到: {self._counter}"
        elif action == "reset":
            self._counter = 0
            return "计数器已重置"
        elif action == "get":
            return f"当前计数: {self._counter}"
        else:
            return f"未知操作: {action}"
