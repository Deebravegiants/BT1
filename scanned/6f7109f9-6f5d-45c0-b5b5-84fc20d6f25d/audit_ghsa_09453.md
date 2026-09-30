# [H] pgAdmin 4 has deserialization of untrusted data in its FileBackedSessionManager

## Summary
Severity: High
Advisory: GHSA-4rhg-h8f2-v4jm
CVE: CVE-2026-7818
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-4rhg-h8f2-v4jm
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
Deserialization of untrusted data (CWE-502) in pgAdmin 4 FileBackedSessionManager.

The session manager performed unsafe deserialization of session-file contents (using Python's standard object-serialization module) before performing any HMAC integrity check. Any file dropped into the sessions directory was deserialized unconditionally. An authenticated user with write access to the sessions directory (whether by misconfiguration or in combination with another path-traversal flaw) could plant a crafted serialized payload to achieve operating-system level remote code execution under the pgAdmin process identity.

Fix prepends a 64-byte hex SHA-256 HMAC over the session body, computed with SECRET_KEY, and verifies it via hmac.compare_digest before any deserialization. The check is raised (rather than asserted) on empty SECRET_KEY so it is not stripped under -O.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7818
- https://github.com/pgadmin-org/pgadmin4/issues/9901
- https://github.com/pgadmin-org/pgadmin4/commit/30a890337
- https://github.com/pgadmin-org/pgadmin4
