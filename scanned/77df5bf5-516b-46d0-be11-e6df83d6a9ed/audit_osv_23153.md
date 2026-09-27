# [M] CVE-2022-43699

## Summary
Severity: Medium
Advisory: CVE-2022-43699
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-04-15
Source: https://osv.dev/vulnerability/CVE-2022-43699
Type: osv

## Details
OX App Suite before 7.10.6-rev30 allows SSRF because e-mail account discovery disregards the deny-list and thus can be attacked by an adversary who controls the DNS records of an external domain (found in the host part of an e-mail address).

## References
- https://open-xchange.com
- https://seclists.org/fulldisclosure/2023/Feb/3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43699.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43699
