# [M] Grav before 2.0.18 Remote Code Execution via sort filter

## Summary
Severity: Medium
Advisory: CVE-2026-85604
Aliases: GHSA-p6qj-p5m7-f62h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85604
Type: osv

## Details
Grav before 2.0.18 (affected versions <= 2.0.17) contains a remote code execution vulnerability in the Twig sort filter. The sortFunc wrapper in GravExtension.php hardcodes Twig's isSandboxed argument to false, so unlike |map/|filter/|reduce, |sort accepts a plain function name inside the sandbox; the remaining denylist misses spl_autoload, which performs a PHP include. An authenticated user with only page-write rights (admin.pages or api.pages.write) can supply a crafted payload (e.g., via form frontmatter rendered by the Email plugin) that invokes spl_autoload through the sort filter, resulting in arbitrary PHP execution as the web server user.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85604.json
- https://github.com/getgrav/grav/security/advisories/GHSA-p6qj-p5m7-f62h
- https://nvd.nist.gov/vuln/detail/CVE-2026-85604
- https://www.vulncheck.com/advisories/grav-before-2.0.19-remote-code-execution-via-sort-filter
