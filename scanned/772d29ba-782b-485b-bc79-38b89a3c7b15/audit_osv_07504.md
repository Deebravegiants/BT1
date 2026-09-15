# [H] BIT-sqlite-2025-29087

## Summary
Severity: High
Advisory: BIT-sqlite-2025-29087
Aliases: CVE-2025-29087
Ecosystem: Bitnami
Published: 2025-04-11
Source: https://osv.dev/vulnerability/BIT-sqlite-2025-29087
Type: osv

## Affected
- Bitnami: `sqlite` — affected >=3.44.0 <3.49.1

## Details
In SQLite 3.44.0 through 3.49.0 before 3.49.1, the concat_ws() SQL function can cause memory to be written beyond the end of a malloc-allocated buffer. If the separator argument is attacker-controlled and has a large string (e.g., 2MB or more), an integer overflow occurs in calculating the size of the result buffer, and thus malloc may not allocate enough memory.

## References
- https://gist.github.com/ylwango613/a44a29f1ef074fa783e29f04a0afd62a
- https://nvd.nist.gov/vuln/detail/CVE-2025-29087
- https://sqlite.org/releaselog/3_49_1.html
- https://www.sqlite.org/cves.html
- https://sqlite.org/src/info/498e3f1cf57f164f
