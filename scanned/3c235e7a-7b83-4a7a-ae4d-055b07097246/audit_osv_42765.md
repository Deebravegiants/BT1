# [M] mealie - DNS-Rebinding TOCTOU in SSRF Guard Allows Internal Network and Cloud Metadata Access

## Summary
Severity: Medium
Advisory: CVE-2026-71210
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71210
Type: osv

## Details
Mealie's AsyncSafeTransport SSRF guard (mealie/pkgs/safehttp/transport.py) resolves a target hostname once, checks the resolved IP against private-range rules, but then issues the actual outbound HTTP request using the original hostname, which the underlying async transport re-resolves independently.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71210.json
- https://github.com/mealie-recipes/mealie
- https://nvd.nist.gov/vuln/detail/CVE-2026-71210
