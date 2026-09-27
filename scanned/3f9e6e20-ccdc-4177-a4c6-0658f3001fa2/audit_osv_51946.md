# [M] CVE-2021-46195

## Summary
Severity: Medium
Advisory: CVE-2021-46195
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-46195
Type: osv

## Details
GCC v12.0 was discovered to contain an uncontrolled recursion via the component libiberty/rust-demangle.c. This vulnerability allows attackers to cause a Denial of Service (DoS) by consuming excessive CPU and memory resources.

## References
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=103841
