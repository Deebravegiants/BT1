# [H] tty: n_gsm: require CAP_NET_ADMIN to attach N_GSM0710 ldisc

## Summary
Severity: High
Advisory: CVE-2023-52880
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2023-52880
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.155, >=5.16.0 <6.1.86

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: n_gsm: require CAP_NET_ADMIN to attach N_GSM0710 ldisc

Any unprivileged user can attach N_GSM0710 ldisc, but it requires
CAP_NET_ADMIN to create a GSM network anyway.

Require initial namespace CAP_NET_ADMIN to do that.

## References
- https://git.kernel.org/stable/c/2b85977977cbd120591b23c2450e90a5806a7167
- https://git.kernel.org/stable/c/2d154a54c58f9c8375bfbea9f7e51ba3bfb2e43a
- https://git.kernel.org/stable/c/67c37756898a5a6b2941a13ae7260c89b54e0d88
- https://git.kernel.org/stable/c/7a529c9023a197ab3bf09bb95df32a3813f7ba58
- https://git.kernel.org/stable/c/7d303dee473ba3529d75b63491e9963342107bed
- https://git.kernel.org/stable/c/ada28eb4b9561aab93942f3224a2e41d76fe57fa
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52880.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52880
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
