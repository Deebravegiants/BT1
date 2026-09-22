# [M] CVE-2019-7282

## Summary
Severity: Medium
Advisory: CVE-2019-7282
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-01-31
Source: https://osv.dev/vulnerability/CVE-2019-7282
Type: osv

## Details
In NetKit through 0.17, rcp.c in the rcp client allows remote rsh servers to bypass intended access restrictions via the filename of . or an empty filename. The impact is modifying the permissions of the target directory on the client side. This is similar to CVE-2018-20685.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DU33YVEDGFDMAZPSRQTRVKSKG4FAX7QB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FSEX3TKX2DBUKG4A7VJFDLSMZIBJQZ3G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NA24VQJATZWYV42JG2PQUW7IHIZS7UKP/
- https://lists.debian.org/debian-lts-announce/2021/11/msg00016.html
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://bugs.debian.org/920486
