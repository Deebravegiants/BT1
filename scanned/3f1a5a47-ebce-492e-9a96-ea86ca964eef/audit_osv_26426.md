# [H] arm64/sme: Set new vector length before reallocating

## Summary
Severity: High
Advisory: CVE-2023-53184
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53184
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.42 <6.1.43, >=6.4.7 <6.4.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64/sme: Set new vector length before reallocating

As part of fixing the allocation of the buffer for SVE state when changing
SME vector length we introduced an immediate reallocation of the SVE state,
this is also done when changing the SVE vector length for consistency.
Unfortunately this reallocation is done prior to writing the new vector
length to the task struct, meaning the allocation is done with the old
vector length and can lead to memory corruption due to an undersized buffer
being used.

Move the update of the vector length before the allocation to ensure that
the new vector length is taken into account.

For some reason this isn't triggering any problems when running tests on
the arm64 fixes branch (even after repeated tries) but is triggering
issues very often after merge into mainline.

## References
- https://git.kernel.org/stable/c/05d881b85b48c7ac6a7c92ce00aa916c4a84d052
- https://git.kernel.org/stable/c/356e711640aea6ed145da9407499388b45264cb4
- https://git.kernel.org/stable/c/807ada0e4aa3c9090c66009a99fa530c462012c9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53184.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53184
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
