# [M] ajenti.plugin.core has race conditions in 2FA

## Summary
Severity: Medium
Advisory: GHSA-8647-755q-fw9p
CVE: CVE-2026-40178
CWE: CWE-287, CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-8647-755q-fw9p
Type: github-advisory

## Affected
- PyPI: `ajenti.plugin.core` — affected >=0 <0.112

## Details
### Impact

If the 2FA was activated, it was possible during a short moment after the authentication of an user to bypass its authentication.

### Patches

This is fixed in the version 0.112. Users should upgrade to this version as soon as possible.

## References
- https://github.com/ajenti/ajenti/security/advisories/GHSA-8647-755q-fw9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-40178
- https://github.com/ajenti/ajenti
