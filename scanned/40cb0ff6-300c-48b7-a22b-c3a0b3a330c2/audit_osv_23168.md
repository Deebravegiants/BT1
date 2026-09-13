# [H] CVE-2022-44232

## Summary
Severity: High
Advisory: CVE-2022-44232
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-26
Source: https://osv.dev/vulnerability/CVE-2022-44232
Type: osv

## Details
libming 0.4.8 0.4.8 is vulnerable to Buffer Overflow. In getInt() in decompile.c unknown type may lead to denial of service. This is a different vulnerability than CVE-2018-9132 and CVE-2018-20427.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/44xxx/CVE-2022-44232.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-44232
- https://github.com/huanglei3/libming_crashes.git
