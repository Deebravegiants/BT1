# [H] Allowing long password leads to denial of service in polonel/trudesk in polonel/trudesk

## Summary
Severity: High
Advisory: CVE-2022-1728
CVSS: 7.6 (CVSS:3.0/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-05-16
Source: https://osv.dev/vulnerability/CVE-2022-1728
Type: osv

## Details
Allowing long password leads to denial of service in polonel/trudesk in GitHub repository polonel/trudesk prior to 1.2.2. This vulnerability can be abused by doing a DDoS attack for which genuine users will not able to access resources/applications.

## References
- https://huntr.dev/bounties/3c6cb129-6995-4722-81b5-af052572b519
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1728.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1728
- https://github.com/polonel/trudesk/commit/e836d04d16787c2c9c72e7bf011cf396d1f73c19
