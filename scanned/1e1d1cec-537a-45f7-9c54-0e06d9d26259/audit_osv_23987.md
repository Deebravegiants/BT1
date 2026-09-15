# [H] s390: avoid using global register for current_stack_pointer

## Summary
Severity: High
Advisory: CVE-2022-49804
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49804
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390: avoid using global register for current_stack_pointer

Commit 30de14b1884b ("s390: current_stack_pointer shouldn't be a
function") made current_stack_pointer a global register variable like
on many other architectures. Unfortunately on s390 it uncovers old
gcc bug which is fixed only since gcc-9.1 [gcc commit 3ad7fed1cc87
("S/390: Fix PR89775. Stackpointer save/restore instructions removed")]
and backported to gcc-8.4 and later. Due to this bug gcc versions prior
to 8.4 generate broken code which leads to stack corruptions.

Current minimal gcc version required to build the kernel is declared
as 5.1. It is not possible to fix all old gcc versions, so work
around this problem by avoiding using global register variable for
current_stack_pointer.

## References
- https://git.kernel.org/stable/c/a478952a8ac44e32316dc046a063a7dc34825aa6
- https://git.kernel.org/stable/c/e3c11025bcd2142a61abe5806b2f86a0e78118df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49804.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49804
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
