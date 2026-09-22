# [H] Apache Impala: Secrets Exfiltration via SSRF

## Summary
Severity: High
Advisory: CVE-2026-57866
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-57866
Type: osv

## Details
Server side request forgery in Apache Impala versions 4.4.x and 4.5.x.  Authenticated Impala users with permissions to execute the ai_generate_text() function can exfiltrate secrets provided by the credential providers configured in the `hadoop.security.credential.provider.path` property of `core-site.xml`. The secret's key must be known to the user.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57866.json
- https://lists.apache.org/thread/nnk4660cbs6dmmkch7ch7wwb3g9myw7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-57866
