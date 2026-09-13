# [M] regulator: da9063: better fix null deref with partial DT

## Summary
Severity: Medium
Advisory: CVE-2023-53364
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53364
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.7 <6.4.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: da9063: better fix null deref with partial DT

Two versions of the original patch were sent but V1 was merged instead
of V2 due to a mistake.

So update to V2.

The advantage of V2 is that it completely avoids dereferencing the pointer,
even just to take the address, which may fix problems with some compilers.
Both versions work on my gcc 9.4 but use the safer one.

## References
- https://git.kernel.org/stable/c/30c694fd4a99fbbc4115d180156ca01b60953371
- https://git.kernel.org/stable/c/aa402a3b553bd4829f4504058d53b0351c66c9d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53364.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53364
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
