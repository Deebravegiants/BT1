# [H] nilfs2: fix kernel bug on rename operation of broken directory

## Summary
Severity: High
Advisory: CVE-2024-41034
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41034
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.30 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix kernel bug on rename operation of broken directory

Syzbot reported that in rename directory operation on broken directory on
nilfs2, __block_write_begin_int() called to prepare block write may fail
BUG_ON check for access exceeding the folio/page size.

This is because nilfs_dotdot(), which gets parent directory reference
entry ("..") of the directory to be moved or renamed, does not check
consistency enough, and may return location exceeding folio/page size for
broken directories.

Fix this issue by checking required directory entries ("." and "..") in
the first chunk of the directory in nilfs_dotdot().

## References
- https://git.kernel.org/stable/c/1a8879c0771a68d70ee2e5e66eea34207e8c6231
- https://git.kernel.org/stable/c/24c1c8566a9b6be51f5347be2ea76e25fc82b11e
- https://git.kernel.org/stable/c/298cd810d7fb687c90a14d8f9fd1b8719a7cb8a5
- https://git.kernel.org/stable/c/60f61514374e4a0c3b65b08c6024dd7e26150bfd
- https://git.kernel.org/stable/c/7000b438dda9d0f41a956fc9bffed92d2eb6be0d
- https://git.kernel.org/stable/c/a9a466a69b85059b341239766a10efdd3ee68a4b
- https://git.kernel.org/stable/c/a9e1ddc09ca55746079cc479aa3eb6411f0d99d4
- https://git.kernel.org/stable/c/ff9767ba2cb949701e45e6e4287f8af82986b703
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41034.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41034
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
