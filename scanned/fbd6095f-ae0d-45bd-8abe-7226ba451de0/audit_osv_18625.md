# [M] CVE-2020-29159

## Summary
Severity: Medium
Advisory: CVE-2020-29159
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-29159
Type: osv

## Details
An issue was discovered in Zammad before 3.5.1. The default signup Role (for newly created Users) can be a privileged Role, if configured by an admin. This behvaior was unintended.

## References
- https://zammad.com/en/advisories/zaa-2020-22
- https://github.com/zammad/zammad/commit/f0462d4c20c2968b52b5dc6a585f26c0409b4fc4
