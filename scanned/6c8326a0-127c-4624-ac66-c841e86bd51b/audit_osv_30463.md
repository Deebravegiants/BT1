# [H] CVE-2024-52949

## Summary
Severity: High
Advisory: CVE-2024-52949
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-16
Source: https://osv.dev/vulnerability/CVE-2024-52949
Type: osv

## Details
iptraf-ng 1.2.1 has a stack-based buffer overflow. In src/ifaces.c, the strcpy function consistently fails to control the size, and it is consequently possible to overflow memory on the stack.

## References
- https://github.com/iptraf-ng/iptraf-ng/releases/tag/v1.2.1
- https://www.gruppotim.it/it/footer/red-team.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52949.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52949
