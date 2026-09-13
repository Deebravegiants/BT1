# [C] CVE-2020-17528

## Summary
Severity: Critical
Advisory: CVE-2020-17528
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-17528
Type: osv

## Details
Out-of-bounds Write vulnerability in TCP stack of Apache NuttX (incubating) versions up to and including 9.1.0 and 10.0.0 allows attacker to corrupt memory by supplying arbitrary urgent data pointer offsets within TCP packets including beyond the length of the packet.

## References
- http://www.openwall.com/lists/oss-security/2020/12/09/4
- https://lists.apache.org/thread.html/r7f4215aba288660b41b7e731b6262c8275fa476e91e527a74d2888ea%40%3Cdev.nuttx.apache.org%3E
