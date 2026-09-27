# [H] rcu: Fix buffer overflow in print_cpu_stall_info()

## Summary
Severity: High
Advisory: CVE-2024-38576
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38576
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rcu: Fix buffer overflow in print_cpu_stall_info()

The rcuc-starvation output from print_cpu_stall_info() might overflow the
buffer if there is a huge difference in jiffies difference.  The situation
might seem improbable, but computers sometimes get very confused about
time, which can result in full-sized integers, and, in this case,
buffer overflow.

Also, the unsigned jiffies difference is printed using %ld, which is
normally for signed integers.  This is intentional for debugging purposes,
but it is not obvious from the code.

This commit therefore changes sprintf() to snprintf() and adds a
clarifying comment about intention of %ld format.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/3758f7d9917bd7ef0482c4184c0ad673b4c4e069
- https://git.kernel.org/stable/c/4c3e2ef4d8ddd313c8ce3ac30505940bea8d6257
- https://git.kernel.org/stable/c/9351e1338539cb7f319ffc1210fa9b2aa27384b5
- https://git.kernel.org/stable/c/afb39909bfb5c08111f99e21bf5be7505f59ff1c
- https://git.kernel.org/stable/c/e2228ed3fe7aa838fba87c79a76fb1ad9ea47138
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38576.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
