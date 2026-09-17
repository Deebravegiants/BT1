# [M] Python Liquid: Infinite loop when parsing malformed `{% case %}` tags

## Summary
Severity: Medium
Advisory: GHSA-vq2f-vcc9-j8mv
CVE: CVE-2026-55865
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-vq2f-vcc9-j8mv
Type: github-advisory

## Affected
- PyPI: `python-liquid` — affected >=0 <2.2.1

## Details
### Impact
Given a malformed `{% case %}` tag without associated `{% when %}` or `{% else %}` block, and no terminating `{% endcase %}` tag, Python Liquid hangs in an infinite loop at parse time. This allows malicious template authors to craft templates for a denial of service attack.

### Patches
The issue is fixed in version 2.2.1 with the correction of the `liquid.TokenStream.eof` attribute. The `kind` and `value` of the special EOF token are now the same, so either can be tested against `liquid.token.TOKEN_EOF`.

### Workarounds
Manually correct the definition of `liquid.TokenStream.eof` before parsing any templates.

```python
import liquid
from liquid.token import TOKEN_EOF

liquid.stream.TokenStream.eof = liquid.Token(TOKEN_EOF, TOKEN_EOF, -1, "")

# ...
```

## References
- https://github.com/jg-rp/liquid/security/advisories/GHSA-vq2f-vcc9-j8mv
- https://github.com/jg-rp/liquid
