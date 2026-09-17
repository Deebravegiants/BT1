# [M] Crafted backend URLs in Lura Project

## Summary
Severity: Medium
Advisory: CVE-2022-1561
CVSS: 4.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2022-08-01
Source: https://osv.dev/vulnerability/CVE-2022-1561
Type: osv

## Details
Lura and KrakenD-CE versions older than v2.0.2 and KrakenD-EE versions older than v2.0.0 do not sanitize URL parameters correctly, allowing a malicious user to alter the backend URL defined for a pipe when remote users send crafty URL requests. The vulnerability does not affect KrakenD itself, but the consumed backend might be vulnerable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1561.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1561
- https://www.incibe-cert.es/en/early-warning/security-advisories/crafted-backend-urls-lura-project
- https://www.krakend.io/blog/cve-2022-1561-crafted-backend-urls/
