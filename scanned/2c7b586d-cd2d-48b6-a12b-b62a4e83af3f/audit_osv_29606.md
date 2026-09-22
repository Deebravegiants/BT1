# [H] binfmt_flat: Fix corruption when not offsetting data start

## Summary
Severity: High
Advisory: CVE-2024-44966
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44966
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.165, >=5.16.0 <6.1.106, >=6.2.0 <6.6.47, >=6.7.0 <6.10.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

binfmt_flat: Fix corruption when not offsetting data start

Commit 04d82a6d0881 ("binfmt_flat: allow not offsetting data start")
introduced a RISC-V specific variant of the FLAT format which does
not allocate any space for the (obsolete) array of shared library
pointers. However, it did not disable the code which initializes the
array, resulting in the corruption of sizeof(long) bytes before the DATA
segment, generally the end of the TEXT segment.

Introduce MAX_SHARED_LIBS_UPDATE which depends on the state of
CONFIG_BINFMT_FLAT_NO_DATA_START_OFFSET to guard the initialization of
the shared library pointer region so that it will only be initialized
if space is reserved for it.

## References
- https://git.kernel.org/stable/c/3a684499261d0f7ed5ee72793025c88c2276809c
- https://git.kernel.org/stable/c/3eb3cd5992f7a0c37edc8d05b4c38c98758d8671
- https://git.kernel.org/stable/c/49df34d2b7da9e57c839555a2f7877291ce45ad1
- https://git.kernel.org/stable/c/9350ba06ee61db392c486716ac68ecc20e030f7c
- https://git.kernel.org/stable/c/af65d5383854cc3f172a7d0843b628758bf462c8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44966.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44966
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
