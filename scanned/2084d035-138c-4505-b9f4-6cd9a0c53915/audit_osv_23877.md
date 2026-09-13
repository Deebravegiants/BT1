# [M] ip: Fix data-races around sysctl_ip_fwd_use_pmtu.

## Summary
Severity: Medium
Advisory: CVE-2022-49604
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49604
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip: Fix data-races around sysctl_ip_fwd_use_pmtu.

While reading sysctl_ip_fwd_use_pmtu, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/60c158dc7b1f0558f6cadd5b50d0386da0000d50
- https://git.kernel.org/stable/c/7828309df0f89419a9349761a37c7d1b0da45697
- https://git.kernel.org/stable/c/93fbc06da1d819f3981a7bd7928c3641ea67b364
- https://git.kernel.org/stable/c/b96ed5ccb09ae71103023ed13acefb194f609794
- https://git.kernel.org/stable/c/e364b5f6ffbfc457a997ad09a7baa16c19581edc
- https://git.kernel.org/stable/c/eb15262128b793e4b1d1c4514d3e6d19c3959764
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49604.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49604
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
