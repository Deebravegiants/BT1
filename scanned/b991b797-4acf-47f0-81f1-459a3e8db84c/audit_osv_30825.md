# [H] net: af_can: do not leave a dangling sk pointer in can_create()

## Summary
Severity: High
Advisory: CVE-2024-56603
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56603
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: af_can: do not leave a dangling sk pointer in can_create()

On error can_create() frees the allocated sk object, but sock_init_data()
has already attached it to the provided sock object. This will leave a
dangling sk pointer in the sock object and may cause use-after-free later.

## References
- https://git.kernel.org/stable/c/1fe625f12d090d69f3f084990c7e4c1ff94bfe5f
- https://git.kernel.org/stable/c/5947c9ac08f0771ea8ed64186b0d52e9029cb6c0
- https://git.kernel.org/stable/c/811a7ca7320c062e15d0f5b171fe6ad8592d1434
- https://git.kernel.org/stable/c/884ae8bcee749be43a071d6ed2d89058dbd2425c
- https://git.kernel.org/stable/c/8df832e6b945e1ba61467d7f1c9305e314ae92fe
- https://git.kernel.org/stable/c/ce39b5576785bb3e66591145aad03d66bc3e778d
- https://git.kernel.org/stable/c/db207d19adbac96058685f6257720906ad41d215
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56603.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56603
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
