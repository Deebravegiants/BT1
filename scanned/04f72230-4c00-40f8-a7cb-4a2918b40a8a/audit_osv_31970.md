# [M] arcnet: Add NULL check in com20020pci_probe()

## Summary
Severity: Medium
Advisory: CVE-2025-22054
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22054
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.292, >=5.5.0 <5.10.236, >=5.11.0 <5.15.180, >=5.16.0 <6.1.134, >=6.2.0 <6.6.87, >=6.7.0 <6.13.11, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

arcnet: Add NULL check in com20020pci_probe()

devm_kasprintf() returns NULL when memory allocation fails. Currently,
com20020pci_probe() does not check for this case, which results in a
NULL pointer dereference.

Add NULL check after devm_kasprintf() to prevent this issue and ensure
no resources are left allocated.

## References
- https://git.kernel.org/stable/c/661cf5d102949898c931e81fd4e1c773afcdeafa
- https://git.kernel.org/stable/c/887226163504494ea7e58033a97c2d2ab12e05d4
- https://git.kernel.org/stable/c/905a34dc1ad9a53a8aaaf8a759ea5dbaaa30418d
- https://git.kernel.org/stable/c/a654f31b33515d39bb56c75fd8b26bef025ced7e
- https://git.kernel.org/stable/c/be8a0decd0b59a52a07276f9ef3b33ef820b2179
- https://git.kernel.org/stable/c/ebebeb58d48e25525fa654f2c53a24713fe141c3
- https://git.kernel.org/stable/c/ececf8eff6c25acc239fa8f0fd837c76bc770547
- https://git.kernel.org/stable/c/ef8b29398ea6061ac8257f3e45c9be45cc004ce2
- https://git.kernel.org/stable/c/fda8c491db2a90ff3e6fbbae58e495b4ddddeca3
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22054.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22054
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
