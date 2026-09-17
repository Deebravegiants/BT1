# [M] CVE-2019-17639

## Summary
Severity: Medium
Advisory: CVE-2019-17639
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-07-15
Source: https://osv.dev/vulnerability/CVE-2019-17639
Type: osv

## Details
In Eclipse OpenJ9 prior to version 0.21 on Power platforms, calling the System.arraycopy method with a length longer than the length of the source or destination array can, in certain specially crafted code patterns, cause the current method to return prematurely with an undefined return value. This allows whatever value happens to be in the return register at that time to be used as if it matches the method's declared return type.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=563998
