# [H] CVE-2017-17432

## Summary
Severity: High
Advisory: CVE-2017-17432
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-06
Source: https://osv.dev/vulnerability/CVE-2017-17432
Type: osv

## Details
OpenAFS 1.x before 1.6.22 does not properly validate Rx ack packets, which allows remote attackers to cause a denial of service (system crash or application crash) via crafted fields, as demonstrated by an integer underflow and assertion failure for a small MTU value.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00016.html
- https://www.debian.org/security/2017/dsa-4067
- https://www.openafs.org/pages/security/OPENAFS-SA-2017-001.txt
- https://bugs.debian.org/883602
