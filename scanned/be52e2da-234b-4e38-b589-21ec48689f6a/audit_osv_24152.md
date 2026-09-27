# [H] staging: vt6655: fix some erroneous memory clean-up loops

## Summary
Severity: High
Advisory: CVE-2022-50355
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50355
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.262, >=4.20.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: vt6655: fix some erroneous memory clean-up loops

In some initialization functions of this driver, memory is allocated with
'i' acting as an index variable and increasing from 0. The commit in
"Fixes" introduces some clean-up codes in case of allocation failure,
which free memory in reverse order with 'i' decreasing to 0. However,
there are some problems:
  - The case i=0 is left out. Thus memory is leaked.
  - In case memory allocation fails right from the start, the memory
    freeing loops will start with i=-1 and invalid memory locations will
    be accessed.

One of these loops has been fixed in commit c8ff91535880 ("staging:
vt6655: fix potential memory leak"). Fix the remaining erroneous loops.

## References
- https://git.kernel.org/stable/c/2a2db520e3ca5aafba7c211abfd397666c9b5f9d
- https://git.kernel.org/stable/c/637672a71f5016a40b0a6c0f3c8ad25eacedc8c3
- https://git.kernel.org/stable/c/88b9cc60f26e8a05d1ddbddf91b09ca2915f20e0
- https://git.kernel.org/stable/c/95ac62e8545be2b0a8cae0beef7c682e2e470e48
- https://git.kernel.org/stable/c/a9e9806d1c315bc50dce05479a079b9a104474b8
- https://git.kernel.org/stable/c/ed11b73c963292e7b49c0f37025c58ed3b7921d6
- https://git.kernel.org/stable/c/f19e5b7df54590c831f350381963f25585c8f7d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50355.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
