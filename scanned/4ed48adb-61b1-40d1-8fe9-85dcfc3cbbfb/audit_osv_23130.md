# [M] CVE-2022-43552

## Summary
Severity: Medium
Advisory: CVE-2022-43552
Aliases: CURL-CVE-2022-43552
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-09
Source: https://osv.dev/vulnerability/CVE-2022-43552
Type: osv

## Details
A use after free vulnerability exists in curl <7.87.0. Curl can be asked to *tunnel* virtually all protocols it supports through an HTTP proxy. HTTP proxies can (and often do) deny such tunnel operations. When getting denied to tunnel the specific protocols SMB or TELNET, curl would use a heap-allocated struct after it had been freed, in its transfer shutdown code path.

## References
- https://hackerone.com/reports/1764858
- https://support.apple.com/kb/HT213670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43552.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43552
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230214-0002/
- http://seclists.org/fulldisclosure/2023/Mar/17
