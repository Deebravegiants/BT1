# [C] Microweber CMS 2.0.20 Server-Side Template Injection via Mail Templates

## Summary
Severity: Critical
Advisory: CVE-2026-65693
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-65693
Type: osv

## Details
Microweber CMS through 2.0.20 contains a server-side template injection vulnerability that allows authenticated administrators to achieve arbitrary OS command execution by injecting Twig expressions into mail templates. Attackers can exploit the unsandboxed Twig environment in TwigView::render(), which lacks SandboxExtension or a SecurityPolicy, to inject malicious expressions such as filter('system') into mail template bodies stored unsanitized in the database, causing automatic payload execution on each subsequent application event that triggers a mail dispatch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65693.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65693
- https://www.vulncheck.com/advisories/microweber-cms-server-side-template-injection-via-mail-templates
- https://github.com/microweber/microweber
- https://gist.github.com/W40X/584f4b088d310bc5280cc74bbf97831a
