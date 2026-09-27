# [M] CVE-2025-47203

## Summary
Severity: Medium
Advisory: CVE-2025-47203
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2025-05-07
Source: https://osv.dev/vulnerability/CVE-2025-47203
Type: osv

## Details
dbclient in Dropbear SSH before 2025.88 allows command injection via an untrusted hostname argument, because a shell is used.

## References
- http://www.openwall.com/lists/oss-security/2025/05/09/4
- http://www.openwall.com/lists/oss-security/2025/05/12/6
- http://www.openwall.com/lists/oss-security/2025/05/13/1
- http://www.openwall.com/lists/oss-security/2025/05/13/10
- http://www.openwall.com/lists/oss-security/2025/05/13/3
- https://github.com/mkj/dropbear/blob/master/CHANGES
- https://github.com/mkj/dropbear/blob/master/src/cli-main.c
- https://lists.debian.org/debian-lts-announce/2025/05/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47203.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47203
