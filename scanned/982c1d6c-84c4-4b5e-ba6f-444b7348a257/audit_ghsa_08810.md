# [H] pgAdmin 4: OS command injection vulnerability in Import/Export query export

## Summary
Severity: High
Advisory: GHSA-j74f-g7vx-fh4x
CVE: CVE-2026-7816
CWE: CWE-78, CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-j74f-g7vx-fh4x
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
OS command injection (CWE-78) vulnerability in pgAdmin 4 Import/Export query export.

User-supplied input was interpolated directly into a psql \copy metacommand template without sanitization. An authenticated user could inject ") TO PROGRAM 'cmd'" to break out of the \copy (...) context and achieve arbitrary command execution on the pgAdmin server, or ") TO '/path'" for arbitrary file write. Additional fields (format, on_error, log_verbosity) were also raw-interpolated and exploitable.

Fix adds a parens-balance parser modeled on psql's strtokx tokenizer, allow-lists format/on_error/log_verbosity, rejects null bytes in the query, and tightens type and gating checks.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7816
- https://github.com/pgadmin-org/pgadmin4/issues/9899
- https://github.com/pgadmin-org/pgadmin4/commit/13badc62c
- https://github.com/pgadmin-org/pgadmin4
