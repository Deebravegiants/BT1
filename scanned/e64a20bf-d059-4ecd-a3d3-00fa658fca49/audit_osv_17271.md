# [M] CVE-2020-14214

## Summary
Severity: Medium
Advisory: CVE-2020-14214
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-06-16
Source: https://osv.dev/vulnerability/CVE-2020-14214
Type: osv

## Details
Zammad before 3.3.1, when Domain Based Assignment is enabled, relies on a claimed e-mail address for authorization decisions. An attacker can register a new account that will have access to all tickets of an arbitrary Organization.

## References
- https://zammad.com/news/security-advisory-zaa-2020-12
- https://github.com/zammad/zammad/commit/40148392426f626cb779c76d6bdda0f67bd6069d
