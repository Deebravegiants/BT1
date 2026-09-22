# [H] jfs: don't walk off the end of ealist

## Summary
Severity: High
Advisory: CVE-2024-41017
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41017
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.319, >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: don't walk off the end of ealist

Add a check before visiting the members of ea to
make sure each ea stays within the ealist.

## References
- https://git.kernel.org/stable/c/17440dbc66ab98b410514b04987f61deedb86751
- https://git.kernel.org/stable/c/4e034f7e563ab723b93a59980e4a1bb33198ece8
- https://git.kernel.org/stable/c/6386f1b6a10e5d1ddd03db4ff6dfc55d488852ce
- https://git.kernel.org/stable/c/7e21574195a45fc193555fa40e99fed16565ff7e
- https://git.kernel.org/stable/c/7f91bd0f2941fa36449ce1a15faaa64f840d9746
- https://git.kernel.org/stable/c/d0fa70aca54c8643248e89061da23752506ec0d4
- https://git.kernel.org/stable/c/dbde7bc91093fa9c2410e418b236b70fde044b73
- https://git.kernel.org/stable/c/f4435f476b9bf059cd9e26a69f5b29c768d00375
- https://git.kernel.org/stable/c/fc16776a82e8df97b6c4f9a10ba95aa44cef7ba5
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41017.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41017
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
