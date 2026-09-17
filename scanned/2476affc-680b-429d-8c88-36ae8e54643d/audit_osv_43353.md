# [C] CamaleonCMS 2.9.1 Server-Side Template Injection via test_email Action

## Summary
Severity: Critical
Advisory: CVE-2026-73330
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73330
Type: osv

## Details
CamaleonCMS 2.9.1 contains a server-side template injection vulnerability that allows authenticated administrators to execute arbitrary commands by embedding ERB tags in the email parameter of the test_email settings action, which are evaluated when an SMTP rejection reflects the recipient address back in the exception message rendered as an inline ERB template. Attackers can submit a crafted email parameter containing ERB expressions through the admin settings test_email endpoint, causing the Rails inline template renderer to evaluate attacker-controlled Ruby code and achieve arbitrary command execution as the Rails process user.

## References
- https://enrik-m.github.io/posts/Camaleon-CMS-Vulnerabilties/#44-stored-xss-via-draft-post-title
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73330.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73330
- https://www.vulncheck.com/advisories/camaleoncms-server-side-template-injection-via-test-email-action
- https://github.com/owen2345/camaleon-cms
