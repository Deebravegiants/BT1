# [H] CVE-2019-3500

## Summary
Severity: High
Advisory: CVE-2019-3500
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-02
Source: https://osv.dev/vulnerability/CVE-2019-3500
Type: osv

## Details
aria2c in aria2 1.33.1, when --log is used, can store an HTTP Basic Authentication username and password in a file, which might allow local users to obtain sensitive information by reading this file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/532M22TAOOIY3J4XX4R7BLZHXJRUSBQ2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MUUYDELHRLVE2AFNVR3OJ6ILUKVLY4B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U5OLPTVYHJZJ2MVEXJCNPXBSFPVPE4XX/
- https://lists.debian.org/debian-lts-announce/2019/01/msg00012.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00039.html
- https://usn.ubuntu.com/3965-1/
- https://github.com/aria2/aria2/issues/1329
