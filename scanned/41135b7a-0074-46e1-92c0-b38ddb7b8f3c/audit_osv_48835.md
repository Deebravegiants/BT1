# [H] CVE-2018-15471

## Summary
Severity: High
Advisory: CVE-2018-15471
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/CVE-2018-15471
Type: osv

## Details
An issue was discovered in xenvif_set_hash_mapping in drivers/net/xen-netback/hash.c in the Linux kernel through 4.18.1, as used in Xen through 4.11.x and other products. The Linux netback driver allows frontends to control mapping of requests to request queues. When processing a request to set or change this mapping, some input validation (e.g., for an integer overflow) was missing or flawed, leading to OOB access in hash handling. A malicious or buggy frontend may cause the (usually privileged) backend to make out of bounds memory accesses, potentially resulting in one or more of privilege escalation, Denial of Service (DoS), or information leaks.

## References
- https://usn.ubuntu.com/3819-1/
- https://usn.ubuntu.com/3820-1/
- https://usn.ubuntu.com/3820-2/
- https://usn.ubuntu.com/3820-3/
- https://www.debian.org/security/2018/dsa-4313
- http://xenbits.xen.org/xsa/advisory-270.html
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1607
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
