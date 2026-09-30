# [M] Marshmallow has DoS in Schema.load(many)

## Summary
Severity: Medium
Advisory: GHSA-428g-f7cq-pgp5
CVE: CVE-2025-68480
CWE: CWE-405
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-428g-f7cq-pgp5
Type: github-advisory

## Affected
- PyPI: `marshmallow` — affected >=3.0.0rc1 <3.26.2
- PyPI: `marshmallow` — affected >=4.0.0 <4.1.2

## Details
### Impact

`Schema.load(data, many=True)` is vulnerable to denial of service attacks. A moderately sized request can consume a disproportionate amount of CPU time.

### Patches

4.1.2, 3.26.2

### Workarounds

```py
# Fail fast
def load_many(schema, data, **kwargs):
    if not isinstance(data, list):
        raise ValidationError(['Invalid input type.'])
    return [schema.load(item, **kwargs) for item in data]
```

## References
- https://github.com/marshmallow-code/marshmallow/security/advisories/GHSA-428g-f7cq-pgp5
- https://nvd.nist.gov/vuln/detail/CVE-2025-68480
- https://github.com/marshmallow-code/marshmallow/commit/d24a0c9df061c4daa92f71cf85aca25b83eee508
- https://github.com/marshmallow-code/marshmallow
