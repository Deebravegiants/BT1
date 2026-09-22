# [C] CloudNativePG: Overriding operators can lead to privilege escalation in CloudNativePG for SQL queries without a fixed `search_path`

## Summary
Severity: Critical
Advisory: CVE-2026-55769
Aliases: GHSA-x8c2-3p4r-v9r6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-55769
Type: osv

## Details
CloudNativePG is a platform designed to manage PostgreSQL databases within Kubernetes environments. Prior to 1.28.4 and 1.29.2, CloudNativePG opened superuser connections without pinning search_path in fillDefaultParameters in pkg/management/postgres/pool/profiles.go. A role holding DATABASE OWNER could create overloaded built-in operators in the public schema and change the database or role search_path, causing instance-manager introspection queries such as SELECT COUNT(*) > 0 FROM pg_catalog.pg_extension WHERE extname = $1 to execute attacker-controlled functions as the postgres superuser. The same trust issue affected direct sql.Open("pgx", ...) callsites and the public.user_search SECURITY DEFINER function, enabling PostgreSQL superuser access, operating system command execution through COPY ... FROM PROGRAM, and access to the pod ServiceAccount token. This issue is fixed in versions 1.28.4, 1.29.2, and 1.30.0.

## References
- https://github.com/cloudnative-pg/cloudnative-pg/releases/tag/v1.28.4
- https://github.com/cloudnative-pg/cloudnative-pg/releases/tag/v1.29.2
- https://github.com/cloudnative-pg/cloudnative-pg/releases/tag/v1.30.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55769.json
- https://github.com/cloudnative-pg/cloudnative-pg/security/advisories/GHSA-x8c2-3p4r-v9r6
- https://nvd.nist.gov/vuln/detail/CVE-2026-55769
- https://github.com/cloudnative-pg/cloudnative-pg/commit/02b5c6289b7609dc87fcb1ae9c113160e3d43308
- https://github.com/cloudnative-pg/cloudnative-pg/commit/db38f4d80315c8f1b21bf511ef0f28871820c14d
- https://github.com/cloudnative-pg/cloudnative-pg/commit/e0e2d53adbd907a61f583b1431904b5969f3fd22
- https://github.com/cloudnative-pg/cloudnative-pg/pull/10774
