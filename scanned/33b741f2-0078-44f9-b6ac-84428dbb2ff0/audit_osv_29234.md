# [H] filelock: Fix fcntl/close race recovery compat path

## Summary
Severity: High
Advisory: CVE-2024-41020
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41020
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.13 <4.19.319, >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.102, >=6.2.0 <6.6.43, >=6.7.0 <6.9.12, >=6.10.0 <6.10.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

filelock: Fix fcntl/close race recovery compat path

When I wrote commit 3cad1bc01041 ("filelock: Remove locks reliably when
fcntl/close race is detected"), I missed that there are two copies of the
code I was patching: The normal version, and the version for 64-bit offsets
on 32-bit kernels.
Thanks to Greg KH for stumbling over this while doing the stable
backport...

Apply exactly the same fix to the compat path for 32-bit kernels.

## References
- https://git.kernel.org/stable/c/4c43ad4ab41602201d34c66ac62130fe339d686f
- https://git.kernel.org/stable/c/53e21cfa68a7d12de378b7116c75571f73e0dfa2
- https://git.kernel.org/stable/c/5b0af8e4c70e4b884bb94ff5f0cd49ecf1273c02
- https://git.kernel.org/stable/c/73ae349534ebc377328e7d21891e589626c6e82c
- https://git.kernel.org/stable/c/911cc83e56a2de5a40758766c6a70d6998248860
- https://git.kernel.org/stable/c/a561145f3ae973ebf3e0aee41624e92a6c5cb38d
- https://git.kernel.org/stable/c/ed898f9ca3fa32c56c858b463ceb9d9936cc69c4
- https://git.kernel.org/stable/c/f4d0775c6e2f1340ca0725f0337de149aaa989ca
- https://git.kernel.org/stable/c/f8138f2ad2f745b9a1c696a05b749eabe44337ea
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41020.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
