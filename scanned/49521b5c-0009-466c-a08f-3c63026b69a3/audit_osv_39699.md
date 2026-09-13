# [M] Twig: Sandbox resource exhaustion via unbounded `for` / `range()`

## Summary
Severity: Medium
Advisory: CVE-2026-46627
Aliases: GHSA-923g-j88x-j34q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-46627
Type: osv

## Details
Twig is a template language for PHP. Prior to 3.26.0, the Twig sandbox does not prevent a template from consuming CPU, memory, or wall-clock time, even under the strictest allow-list, allowing untrusted templates to cause resource exhaustion. This issue is addressed in version 3.26.0 by documenting that the sandbox does not protect against resource exhaustion.

## References
- https://github.com/twigphp/Twig/releases/tag/v3.26.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46627.json
- https://github.com/twigphp/Twig/security/advisories/GHSA-923g-j88x-j34q
- https://nvd.nist.gov/vuln/detail/CVE-2026-46627
- https://github.com/twigphp/Twig/commit/6bfa285e2f98651adb7aa480bf83a741d154f09f
