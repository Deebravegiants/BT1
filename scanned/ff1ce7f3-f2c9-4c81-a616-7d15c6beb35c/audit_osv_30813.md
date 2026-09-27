# [M] media: imx-jpeg: Set video drvdata before register video device

## Summary
Severity: Medium
Advisory: CVE-2024-56578
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56578
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.12.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: imx-jpeg: Set video drvdata before register video device

The video drvdata should be set before the video device is registered,
otherwise video_drvdata() may return NULL in the open() file ops, and led
to oops.

## References
- https://git.kernel.org/stable/c/5ade59d28eade49194eb09765afdeb0ba717c39a
- https://git.kernel.org/stable/c/68efeff2f7fccdfedc55f92e92be32997127d16e
- https://git.kernel.org/stable/c/b88556e82dc18cb708744d062770853a2d5095b2
- https://git.kernel.org/stable/c/d2b7ecc26bd5406d5ba927be1748aa99c568696c
- https://git.kernel.org/stable/c/f68bb1210fbea252552d97242757f69a219e942b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56578.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56578
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
