# [M] Twig: Sandbox method allowlist bypass via `Markup` subclass

## Summary
Severity: Medium
Advisory: CVE-2026-46636
Aliases: GHSA-64jr-qjx4-w2fh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-46636
Type: osv

## Details
Twig is a template language for PHP. From version 1.0.0 to before version 3.27.0, SecurityPolicy::checkMethodAllowed() unconditionally whitelists all method calls on instances of Twig\Markup. Twig\Markup is not final, so subclasses inherit the bypass. An application that passes an object of a Markup-derived class into a sandboxed template (typically to mark a chunk of HTML as safe) inadvertently exposes every public method of that subclass to template authors, regardless of the configured allowedMethods list. This issue has been patched in version 3.27.0.

## References
- http://github.com/twigphp/Twig/releases/tag/v3.27.0
- https://security-tracker.debian.org/tracker/CVE-2026-46636
- https://security-tracker.debian.org/tracker/DSA-6311-1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46636.json
- https://github.com/twigphp/Twig/security/advisories/GHSA-64jr-qjx4-w2fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46636
- https://symfony.com/blog/cve-2026-46636-sandbox-filter-tag-and-function-allow-list-bypass-when-sandbox-state-changes-between-renders
