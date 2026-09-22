# [M] tcp: Fix data-races around sysctl_tcp_recovery.

## Summary
Severity: Medium
Advisory: CVE-2022-49574
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49574
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_recovery.

While reading sysctl_tcp_recovery, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/52ee7f5c4811ce6be1becd14d38ba1f8a8a0df81
- https://git.kernel.org/stable/c/92c35113c63306091df9211375eebd0abd8c2160
- https://git.kernel.org/stable/c/a31e2d0cb5cfa2aae3144cac04f25031d5d20fb4
- https://git.kernel.org/stable/c/c7a492db1f7c37c758a66915908677bd8bc5d368
- https://git.kernel.org/stable/c/d8781f7cd04091744f474a2bada74772084b9dc9
- https://git.kernel.org/stable/c/e7d2ef837e14a971a05f60ea08c47f3fed1a36e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49574.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
