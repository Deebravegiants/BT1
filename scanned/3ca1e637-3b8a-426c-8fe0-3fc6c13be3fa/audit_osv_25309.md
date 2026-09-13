# [M] CVE-2023-33656

## Summary
Severity: Medium
Advisory: CVE-2023-33656
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-05-30
Source: https://osv.dev/vulnerability/CVE-2023-33656
Type: osv

## Details
A memory leak vulnerability exists in NanoMQ 0.17.2. The vulnerability is located in the file message.c. An attacker could exploit this vulnerability to cause a denial of service attack by causing the program to consume all available memory resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33656.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33656
- https://github.com/emqx/nanomq/issues/1164
- https://github.com/emqx/nanomq/issues/1165#issuecomment-1515667127
- https://github.com/emqx/nanomq
