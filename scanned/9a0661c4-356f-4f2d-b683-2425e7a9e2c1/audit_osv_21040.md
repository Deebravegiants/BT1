# [H] CVE-2021-40083

## Summary
Severity: High
Advisory: CVE-2021-40083
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-25
Source: https://osv.dev/vulnerability/CVE-2021-40083
Type: osv

## Details
Knot Resolver before 5.3.2 is prone to an assertion failure, triggerable by a remote attacker in an edge case (NSEC3 with too many iterations used for a positive wildcard proof).

## References
- https://gitlab.nic.cz/knot/knot-resolver/-/merge_requests/1169
