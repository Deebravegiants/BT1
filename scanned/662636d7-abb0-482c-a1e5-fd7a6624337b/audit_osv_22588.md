# [M] CVE-2022-32742

## Summary
Severity: Medium
Advisory: CVE-2022-32742
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2022-32742
Type: osv

## Details
A flaw was found in Samba. Some SMB1 write requests were not correctly range-checked to ensure the client had sent enough data to fulfill the write, allowing server memory contents to be written into the file (or printer) instead of client-supplied data. The client cannot control the area of the server memory written to the file (or printer).

## References
- https://www.samba.org/samba/security/CVE-2022-32742.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32742.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32742
- https://security.gentoo.org/glsa/202309-06
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
