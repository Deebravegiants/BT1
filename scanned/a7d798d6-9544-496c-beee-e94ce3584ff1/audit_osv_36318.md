# [H] libceph: make free_choose_arg_map() resilient to partial allocation

## Summary
Severity: High
Advisory: CVE-2026-22991
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-23
Source: https://osv.dev/vulnerability/CVE-2026-22991
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.161, >=6.2.0 <6.6.121, >=6.7.0 <6.12.66, >=6.13.0 <6.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: make free_choose_arg_map() resilient to partial allocation

free_choose_arg_map() may dereference a NULL pointer if its caller fails
after a partial allocation.

For example, in decode_choose_args(), if allocation of arg_map->args
fails, execution jumps to the fail label and free_choose_arg_map() is
called. Since arg_map->size is updated to a non-zero value before memory
allocation, free_choose_arg_map() will iterate over arg_map->args and
dereference a NULL pointer.

To prevent this potential NULL pointer dereference and make
free_choose_arg_map() more resilient, add checks for pointers before
iterating.

## References
- https://git.kernel.org/stable/c/8081faaf089db5280c3be820948469f7c58ef8dd
- https://git.kernel.org/stable/c/851241d3f78a5505224dc21c03d8692f530256b4
- https://git.kernel.org/stable/c/9b3730dabcf3764bfe3ff07caf55e641a0b45234
- https://git.kernel.org/stable/c/c4c2152a858c0ce4d2bff6ca8c1d5b0ef9f2cbdf
- https://git.kernel.org/stable/c/e3fe30e57649c551757a02e1cad073c47e1e075e
- https://git.kernel.org/stable/c/ec1850f663da64842614c86b20fe734be070c2ba
- https://git.kernel.org/stable/c/f21c3fdb96833aac2f533506899fe38c19cf49d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22991.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22991
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
