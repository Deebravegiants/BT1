# [H] rename_tenant returns :ok on a failed rename, enabling cross-tenant access in AshPostgres

## Summary
Severity: High
Advisory: CVE-2026-78699
Aliases: EEF-CVE-2026-78699, GHSA-6fqq-j9c4-5766
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-78699
Type: osv

## Details
Unchecked Return Value vulnerability in ash-project ash_postgres allows a user who can drive a tenant rename to a name that collides with an existing tenant's schema to have their tenant record repointed at that other tenant's live schema, gaining access to its data.

AshPostgres.MultiTenancy.rename_tenant/3 issues the ALTER SCHEMA ... RENAME TO ... with the non-raising Ecto.Adapters.SQL.query/2, discards its {:ok, _} | {:error, _} result, and unconditionally returns :ok. PostgreSQL rejects the rename when the target schema already exists (and on insufficient privilege or lock timeout), but that failure never reaches the caller. The calling manage_tenant update action therefore sees success and commits the tenant row with the new name, which is the schema of a different existing tenant, so subsequent reads and writes for that tenant run against the other tenant's data.

This issue affects ash_postgres: from 0.25.0 before 2.13.0.

## References
- https://cna.erlef.org/cves/CVE-2026-78699.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-78699
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78699.json
- https://github.com/ash-project/ash_postgres/security/advisories/GHSA-6fqq-j9c4-5766
- https://nvd.nist.gov/vuln/detail/CVE-2026-78699
- https://github.com/ash-project/ash_postgres/commit/8544ab15fe45784553c2d2da8ee1a388eee0174b
- https://github.com/ash-project/ash_postgres
