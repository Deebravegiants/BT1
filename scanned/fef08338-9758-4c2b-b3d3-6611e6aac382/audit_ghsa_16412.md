# [H] Potentially untrusted input is rendered as HTML in final output

## Summary
Severity: High
Advisory: GHSA-578p-fxmm-6229
CVE: CVE-2024-26151
CWE: CWE-20, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2024-02-22
Source: https://github.com/advisories/GHSA-578p-fxmm-6229
Type: github-advisory

## Affected
- PyPI: `mjml` — affected >=0.10.0 <0.11.0

## Details
### Impact

All users of mjml-python who insert untrusted data into mjml templates unless that data is checked in a very strict manner. User input like `&lt;script&gt;` would be rendered as `<script>` in the final HTML output.

The attacker must be able to control some data which is later injected in an mjml template which is then send out as email to other users. The attacker could control contents of email messages sent through the platform.

### Patches

The problem has been fixed in version 0.11.0 of this library. Versions before 0.10.0 are not affected by this security issue which was added as part of commit 84c495da20a91640a1ca551ace17df7f3be644aa.


### Workarounds

- Ensure that potentially untrusted user input does not contain any sequences which could be rendered as HTML. 


### References

- Initial issue report by @sh-at-cs in #52

## References
- https://github.com/FelixSchwarz/mjml-python/security/advisories/GHSA-578p-fxmm-6229
- https://nvd.nist.gov/vuln/detail/CVE-2024-26151
- https://github.com/FelixSchwarz/mjml-python/issues/52
- https://github.com/FelixSchwarz/mjml-python/commit/84c495da20a91640a1ca551ace17df7f3be644aa
- https://github.com/FelixSchwarz/mjml-python/commit/8d410b7a500703080bb14ed7e3d2663fe16767e6
- https://github.com/FelixSchwarz/mjml-python
- https://github.com/FelixSchwarz/mjml-python/releases/tag/v0.11.0
