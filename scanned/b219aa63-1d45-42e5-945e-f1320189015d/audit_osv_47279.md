# [H] CVE-2016-2070

## Summary
Severity: High
Advisory: CVE-2016-2070
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-2070
Type: osv

## Details
The tcp_cwnd_reduction function in net/ipv4/tcp_input.c in the Linux kernel before 4.3.5 allows remote attackers to cause a denial of service (divide-by-zero error and system crash) via crafted TCP traffic.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8b8a321ff72c785ed5e8b4cf6eda20b35d427390
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.5
- https://bugzilla.redhat.com/show_bug.cgi?id=1302219
- https://github.com/torvalds/linux/commit/8b8a321ff72c785ed5e8b4cf6eda20b35d427390
- http://www.openwall.com/lists/oss-security/2016/01/25/5
