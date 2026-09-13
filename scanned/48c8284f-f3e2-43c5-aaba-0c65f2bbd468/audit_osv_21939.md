# [C] Improper handling of Length parameter in erudika/scoold

## Summary
Severity: Critical
Advisory: CVE-2022-1543
CVSS: 9.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H)
Published: 2022-04-29
Source: https://osv.dev/vulnerability/CVE-2022-1543
Type: osv

## Details
Improper handling of Length parameter in GitHub repository erudika/scoold prior to 1.49.4. When the text size is large enough the service results in a momentary outage in a production environment. That can lead to memory corruption on the server.

## References
- https://huntr.dev/bounties/9889d435-3b9c-4e9d-93bc-5272e0723f9f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1543.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1543
- https://github.com/erudika/scoold/commit/62a0e92e1486ddc17676a7ead2c07ff653d167ce
