# [C] nvme: avoid double free special payload

## Summary
Severity: Critical
Advisory: CVE-2024-41073
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41073
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.237, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme: avoid double free special payload

If a discard request needs to be retried, and that retry may fail before
a new special payload is added, a double free will result. Clear the
RQF_SPECIAL_LOAD when the request is cleaned.

## References
- https://git.kernel.org/stable/c/1b9fd1265fac85916f90b4648de02adccdb7220b
- https://git.kernel.org/stable/c/882574942a9be8b9d70d13462ddacc80c4b385ba
- https://git.kernel.org/stable/c/ae84383c96d6662c24697ab6b44aae855ab670aa
- https://git.kernel.org/stable/c/c5942a14f795de957ae9d66027aac8ff4fe70057
- https://git.kernel.org/stable/c/e5d574ab37f5f2e7937405613d9b1a724811e5ad
- https://git.kernel.org/stable/c/f3ab45aacd25d957547fb6d115c1574c20964b3b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41073
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
