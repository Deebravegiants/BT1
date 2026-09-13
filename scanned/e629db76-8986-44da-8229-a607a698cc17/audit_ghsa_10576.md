# [M] Weblate: SSRF via the webhook add-on using unprotected fetch_url()

## Summary
Severity: Medium
Advisory: GHSA-f8hv-g549-hwg2
CVE: CVE-2026-39845
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-f8hv-g549-hwg2
Type: github-advisory

## Affected
- PyPI: `Weblate` — affected >=0 <5.17

## Details
### Impact
The webhook add-on did not utilize existing SSRF protection.

### Patches
* https://github.com/WeblateOrg/weblate/pull/18815

### Workarounds
Disabling the add-on would avoid misusing this.

### References
Thanks to @Lihfdgjr for reporting this via GitHub.

## References
- https://github.com/WeblateOrg/weblate/security/advisories/GHSA-f8hv-g549-hwg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39845
- https://github.com/WeblateOrg/weblate/pull/18815
- https://github.com/WeblateOrg/weblate
- https://github.com/pypa/advisory-database/tree/main/vulns/weblate/PYSEC-2026-156.yaml
