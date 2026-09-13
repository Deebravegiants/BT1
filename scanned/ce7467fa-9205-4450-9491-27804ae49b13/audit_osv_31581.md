# [M] Insecure direct object reference

## Summary
Severity: Medium
Advisory: CVE-2025-14881
Aliases: GHSA-r2h2-g46h-8mx8, PYSEC-2026-1803
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:U)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-14881
Type: osv

## Details
Multiple API endpoints allowed access to sensitive files from other users by knowing the UUID of the file that were not intended to be accessible by UUID only.

## References
- https://pypi.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14881.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14881
- https://pretix.eu/about/en/blog/20251218-release-2025-10-1/
- https://github.com/pretix/pretix
