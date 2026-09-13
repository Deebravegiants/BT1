# [C] CVE-2020-17529

## Summary
Severity: Critical
Advisory: CVE-2020-17529
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-17529
Type: osv

## Details
Out-of-bounds Write vulnerability in TCP Stack of Apache NuttX (incubating) versions up to and including 9.1.0 and 10.0.0 allows attacker to corrupt memory by supplying and invalid fragmentation offset value specified in the IP header. This is only impacts builds with both CONFIG_EXPERIMENTAL and CONFIG_NET_TCP_REASSEMBLY build flags enabled.

## References
- http://www.openwall.com/lists/oss-security/2020/12/09/5
- https://lists.apache.org/thread.html/r4d71ae3ab96b589835b94ba7ac4cb88a704e7307bceefeab749366f3%40%3Cdev.nuttx.apache.org%3E
