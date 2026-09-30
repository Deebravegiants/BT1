# [H] CVE-2017-16995

## Summary
Severity: High
Advisory: CVE-2017-16995
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-16995
Type: osv

## Details
The check_alu_op function in kernel/bpf/verifier.c in the Linux kernel through 4.4 allows local users to cause a denial of service (memory corruption) or possibly have unspecified other impact by leveraging incorrect sign extension.

## References
- https://www.exploit-db.com/exploits/45058/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=95a762e2c8c942780948091f8f2a4f32fce1ac6f
- http://openwall.com/lists/oss-security/2017/12/21/2
- http://www.securityfocus.com/bid/102288
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1454
- https://git.kernel.org/pub/scm/linux/kernel/git/tip/tip.git/commit/?id=a6132276ab5dcc38b3299082efeb25b948263adb
- https://github.com/torvalds/linux/commit/95a762e2c8c942780948091f8f2a4f32fce1ac6f
- https://usn.ubuntu.com/3619-1/
- https://www.debian.org/security/2017/dsa-4073
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3633-1/
- https://usn.ubuntu.com/usn/usn-3523-2/
- https://www.exploit-db.com/exploits/44298/
- https://www.exploit-db.com/exploits/45010/
