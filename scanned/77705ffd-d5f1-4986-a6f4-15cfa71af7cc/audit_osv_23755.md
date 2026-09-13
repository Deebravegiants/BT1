# [M] soc: bcm: Check for NULL return of devm_kzalloc()

## Summary
Severity: Medium
Advisory: CVE-2022-49448
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49448
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: bcm: Check for NULL return of devm_kzalloc()

As the potential failure of allocation, devm_kzalloc() may return NULL.  Then
the 'pd->pmb' and the follow lines of code may bring null pointer dereference.

Therefore, it is better to check the return value of devm_kzalloc() to avoid
this confusion.

## References
- https://git.kernel.org/stable/c/36339ea7bae4943be01c8e9545e46e334591fecd
- https://git.kernel.org/stable/c/5650e103bfc70156001615861fb8aafb3947da6e
- https://git.kernel.org/stable/c/b48b98743b568bb219152ba2e15af6ef0d3d8a9b
- https://git.kernel.org/stable/c/b4bd2aafacce48db26b0a213d849818d940556dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49448.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49448
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
