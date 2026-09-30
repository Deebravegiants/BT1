# [M] pinctrl: apple: check devm_kasprintf() returned value

## Summary
Severity: Medium
Advisory: CVE-2024-50069
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-50069
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.114, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: apple: check devm_kasprintf() returned value

devm_kasprintf() can return a NULL pointer on failure but this returned
value is not checked. Fix this lack and check the returned value.

Found by code review.

## References
- https://git.kernel.org/stable/c/0a4d4dbef622ac8796a6665e0080da2685f9220a
- https://git.kernel.org/stable/c/4d2296fb7c80fdc9925d29a8e85d617cad08731a
- https://git.kernel.org/stable/c/665a58fe663ac7a9ea618dc0b29881649324b116
- https://git.kernel.org/stable/c/fad940e2dd789155f99ecafa71a7baf6f96530bc
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50069.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
