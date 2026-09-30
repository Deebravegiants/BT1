# [C] Session hijacking via exposed session signing secret in distributed Checkmk setups

## Summary
Severity: Critical
Advisory: CVE-2025-64998
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2025-64998
Type: osv

## Details
Exposure of session signing secret in Checkmk <2.4.0p23, <2.3.0p45 and 2.2.0 allows an administrator of a remote site with config sync enabled to hijack sessions on the central site by forging session cookies.

## References
- https://checkmk.com/werk/18954
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64998.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64998
