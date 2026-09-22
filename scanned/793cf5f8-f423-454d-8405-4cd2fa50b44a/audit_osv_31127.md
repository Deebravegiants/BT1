# [H] binfmt_flat: Fix integer overflow bug on 32 bit systems

## Summary
Severity: High
Advisory: CVE-2024-58010
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-58010
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.8.0 <5.4.291, >=5.5.0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

binfmt_flat: Fix integer overflow bug on 32 bit systems

Most of these sizes and counts are capped at 256MB so the math doesn't
result in an integer overflow.  The "relocs" count needs to be checked
as well.  Otherwise on 32bit systems the calculation of "full_data"
could be wrong.

	full_data = data_len + relocs * sizeof(unsigned long);

## References
- https://git.kernel.org/stable/c/0b6be54d7386b7addbf9e5947366f94aad046938
- https://git.kernel.org/stable/c/55cf2f4b945f6a6416cc2524ba740b83cc9af25a
- https://git.kernel.org/stable/c/6fb98e0576ea155267e206286413dcb3a3d55c12
- https://git.kernel.org/stable/c/8e8cd712bb06a507b26efd2a56155076aa454345
- https://git.kernel.org/stable/c/95506c7f33452450346fbe2975c1359100f854ca
- https://git.kernel.org/stable/c/a009378af674b808efcca1e2e67916e79ce866b3
- https://git.kernel.org/stable/c/bc8ca18b8ef4648532c001bd6c8151143b569275
- https://git.kernel.org/stable/c/d17ca8f2dfcf423c439859995910a20e38b86f00
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58010.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58010
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
