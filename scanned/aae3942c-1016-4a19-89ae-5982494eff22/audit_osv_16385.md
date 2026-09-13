# [M] CVE-2019-6293

## Summary
Severity: Medium
Advisory: CVE-2019-6293
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-15
Source: https://osv.dev/vulnerability/CVE-2019-6293
Type: osv

## Details
An issue was discovered in the function mark_beginning_as_normal in nfa.c in flex 2.6.4. There is a stack exhaustion problem caused by the mark_beginning_as_normal function making recursive calls to itself in certain scenarios involving lots of '*' characters. Remote attackers could leverage this vulnerability to cause a denial-of-service.

## References
- https://github.com/westes/flex/issues/414
