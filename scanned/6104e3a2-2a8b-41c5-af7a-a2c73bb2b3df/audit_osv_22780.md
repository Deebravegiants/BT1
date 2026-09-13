# [H] CVE-2022-38931

## Summary
Severity: High
Advisory: CVE-2022-38931
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-20
Source: https://osv.dev/vulnerability/CVE-2022-38931
Type: osv

## Details
A Server-Side Request Forgery (SSRF) in fetch_net_file_upload function of baijiacmsV4 v4.1.4 allows remote attackers to force the application to make arbitrary requests via injection of arbitrary URLs into the url parameter.

## References
- https://github.com/zer0yu/CVE_Request/blob/master/baijiacms/baijiacmsv4_ssrf.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/38xxx/CVE-2022-38931.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-38931
