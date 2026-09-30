# [M] Missing Authentication for Critical Function in coolercontrold

## Summary
Severity: Medium
Advisory: CVE-2026-5300
CVSS: 5.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-5300
Type: osv

## Details
Unauthenticated functionality in  CoolerControl/coolercontrold <4.0.0 allows unauthenticated attackers to view and modify potentially sensitive data via HTTP requests

## References
- https://gitlab.com/coolercontrol/coolercontrol/-/blob/3.1.1/coolercontrold/src/api/router.rs?ref_type=tags
- https://gitlab.com/coolercontrol/coolercontrol/-/releases/4.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5300.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5300
