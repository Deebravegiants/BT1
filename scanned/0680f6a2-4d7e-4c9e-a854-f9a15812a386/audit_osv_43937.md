# [C] ArcadeDB before 26.8.1 Remote Code Execution via Groovy Fallback

## Summary
Severity: Critical
Advisory: CVE-2026-76224
Aliases: GHSA-wcm5-4wjm-9wj3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76224
Type: osv

## Details
ArcadeDB before 26.8.1 (arcadedb-gremlin, affected <= 26.7.3) contains a remote code execution vulnerability in its Gremlin query engine. Although the engine defaults to the documented-secure java (gremlin-lang) engine, ArcadeGremlin.executeStatement() silently falls back to the insecure Groovy engine whenever a request carries any query parameter and the query does not parse as gremlin-lang. An authenticated user with any database role, including a read-only reader, can submit a parameterized Gremlin query to trigger the Groovy fallback and execute arbitrary operating system commands as the ArcadeDB server process user.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-wcm5-4wjm-9wj3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76224.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76224
- https://www.vulncheck.com/advisories/arcadedb-before-remote-code-execution-via-groovy-fallback
