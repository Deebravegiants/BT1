# [M] igmp: Fix data-races around sysctl_igmp_qrv.

## Summary
Severity: Medium
Advisory: CVE-2022-49589
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49589
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.19.255, >=4.20.0 <5.4.209, >=5.5.0 <5.10.135, >=5.11.0 <5.15.59, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

igmp: Fix data-races around sysctl_igmp_qrv.

While reading sysctl_igmp_qrv, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

This test can be packed into a helper, so such changes will be in the
follow-up series after net is merged into net-next.

  qrv ?: READ_ONCE(net->ipv4.sysctl_igmp_qrv);

## References
- https://git.kernel.org/stable/c/8ebcc62c738f68688ee7c6fec2efe5bc6d3d7e60
- https://git.kernel.org/stable/c/9eeb3a7702998bdccbfcc37997b5dd9215b9a7f7
- https://git.kernel.org/stable/c/b399ffafffba39f47b731b26a5da1dc0ffc4b3ad
- https://git.kernel.org/stable/c/c2954671010cd1127d1ffa328c6e6f8e99930982
- https://git.kernel.org/stable/c/c721324afc589f8ea54bae04756b150aeaae5fa4
- https://git.kernel.org/stable/c/e20dd1b0e0ea15bee1e528536a0840dba972ca0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49589.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49589
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
