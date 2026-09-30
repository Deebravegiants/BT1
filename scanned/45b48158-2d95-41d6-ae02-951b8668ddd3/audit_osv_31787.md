# [M] can: ctucanfd: handle skb allocation failure

## Summary
Severity: Medium
Advisory: CVE-2025-21775
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21775
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.129, >=6.2.0 <6.6.79, >=6.7.0 <6.12.16, >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: ctucanfd: handle skb allocation failure

If skb allocation fails, the pointer to struct can_frame is NULL. This
is actually handled everywhere inside ctucan_err_interrupt() except for
the only place.

Add the missed NULL check.

Found by Linux Verification Center (linuxtesting.org) with SVACE static
analysis tool.

## References
- https://git.kernel.org/stable/c/84b9ac59978a6a4e0812d1c938fad97306272cef
- https://git.kernel.org/stable/c/9bd24927e3eeb85642c7baa3b28be8bea6c2a078
- https://git.kernel.org/stable/c/b0e592dd46a0a952b41c3bf6c963afdd6a42b526
- https://git.kernel.org/stable/c/e505b83b9ee6aa0ae2f4395f573a66579ae403fb
- https://git.kernel.org/stable/c/e7e2e2318b1f085044126ba553a4e619842fc36d
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21775.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21775
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
