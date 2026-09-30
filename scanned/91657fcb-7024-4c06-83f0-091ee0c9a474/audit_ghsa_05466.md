# [M] Weblate wlc has insecure API key configuration

## Summary
Severity: Medium
Advisory: GHSA-9rp8-h4g8-8766
CVE: CVE-2026-22251
CWE: CWE-200, CWE-922
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-12
Source: https://github.com/advisories/GHSA-9rp8-h4g8-8766
Type: github-advisory

## Affected
- PyPI: `wlc` — affected >=0 <1.17.0

## Details
### Impact
Historically, wlc supported providing unscoped API keys in the setting. This practice was discouraged for years, but the code was never removed. This might cause the API key to be used against different server.

### Patches
* https://github.com/WeblateOrg/wlc/pull/1098

### Workarounds
Remove unscoped `key` from wlc configuration. Only use URL-scoped keys in the `[keys]` sections.

### References
This issue was reported to us by [wh1zee](https://hackerone.com/wh1zee) via HackerOne.

## References
- https://github.com/WeblateOrg/wlc/security/advisories/GHSA-9rp8-h4g8-8766
- https://nvd.nist.gov/vuln/detail/CVE-2026-22251
- https://github.com/WeblateOrg/wlc/pull/1098
- https://github.com/WeblateOrg/wlc/commit/aafdb507a9e66574ade1f68c50c4fe75dbe80797
- https://github.com/WeblateOrg/wlc
