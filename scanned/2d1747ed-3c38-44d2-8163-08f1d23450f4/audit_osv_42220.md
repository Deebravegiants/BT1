# [M] Microweber CMS 2.0.20 Path Traversal via ServeStaticFileController

## Summary
Severity: Medium
Advisory: CVE-2026-65694
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65694
Type: osv

## Details
Microweber CMS through 2.0.20 contains a path traversal vulnerability in the static file controller that allows unauthenticated remote attackers to read arbitrary files by supplying directory traversal sequences in the path query parameter. Attackers can send a single unauthenticated HTTP GET request exploiting the failure of normalize_path() to strip traversal sequences, disclosing sensitive files such as environment configuration files containing credentials and system files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65694.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65694
- https://www.vulncheck.com/advisories/microweber-cms-path-traversal-via-servestaticfilecontroller
- https://github.com/microweber/microweber/pull/1181
- https://github.com/microweber/microweber
