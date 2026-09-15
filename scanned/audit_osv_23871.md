# [M] tcp: Fix data-races around sysctl_tcp_mtu_probing.

## Summary
Severity: Medium
Advisory: CVE-2022-49598
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49598
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_mtu_probing.

While reading sysctl_tcp_mtu_probing, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/77a04845f0d28a3561494a5f3121488470a968a4
- https://git.kernel.org/stable/c/7e8fc428a7f680f1c4994a40e52d7f95a9a93038
- https://git.kernel.org/stable/c/aabe9438fdfe004e021d5a206227ec105dbe2416
- https://git.kernel.org/stable/c/b0920ca09d9ce19980c8391b9002455baa9c1417
- https://git.kernel.org/stable/c/f47d00e077e7d61baf69e46dde3210c886360207
- https://git.kernel.org/stable/c/f966773e13cdd3f12baa90071b7b660f6c633ccb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49598.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
