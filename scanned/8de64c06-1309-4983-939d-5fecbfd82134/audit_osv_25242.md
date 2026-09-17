# [H] Nextcloud Server's brute force protection allows someone to send more requests than intended

## Summary
Severity: High
Advisory: CVE-2023-32320
Aliases: GHSA-qphh-6xh7-vffg
CVSS: 8.7 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-06-22
Source: https://osv.dev/vulnerability/CVE-2023-32320
Type: osv

## Details
Nextcloud Server is a data storage system for Nextcloud, a self-hosted productivity platform. When multiple requests are sent in parallel, all of them were executed even if the amount of faulty requests succeeded the limit by the time the response was sent to the client. This allowed someone to send as many requests the server could handle in parallel to bruteforce protected details instead of the configured limit, default 8. Nextcloud Server versions 25.0.7 and 26.0.2 and Nextcloud Enterprise Server versions 21.0.9.12, 22.2.10.12, 23.0.12.7, 24.0.12.2, 25.0.7 and 26.0.2 contain patches for this issue.

## References
- https://hackerone.com/reports/1918525
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32320.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-qphh-6xh7-vffg
- https://nvd.nist.gov/vuln/detail/CVE-2023-32320
- https://github.com/nextcloud/server/pull/38274
