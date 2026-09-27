# [H] Theft of credentials in Unix client PAGs

## Summary
Severity: High
Advisory: CVE-2024-10394
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-10394
Type: osv

## Details
A local user can bypass the OpenAFS PAG (Process Authentication Group) throttling mechanism in Unix clients, allowing the user to create a PAG using an existing id number, effectively joining the PAG and letting the user steal the credentials in that PAG.

## References
- https://github.com/openafs/openafs/
- https://lists.debian.org/debian-lts-announce/2025/05/msg00019.html
- https://www.openafs.org/pages/security/OPENAFS-SA-2024-001.txt
- https://www.openafs.org/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10394.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10394
