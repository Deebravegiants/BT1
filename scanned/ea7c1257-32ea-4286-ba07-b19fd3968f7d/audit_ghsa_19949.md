# [M] ThinkCMF Stored Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-m9mf-rqx6-2xpc
CVE: CVE-2022-40849
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-01
Source: https://github.com/advisories/GHSA-m9mf-rqx6-2xpc
Type: github-advisory

## Affected
- Packagist: `thinkcmf/thinkcmf` — affected >=0 <6.0.8

## Details
ThinkCMF version 6.0.7 is affected by Stored Cross-Site Scripting (XSS). An attacker who successfully exploited this vulnerability could inject a Persistent XSS payload in the Slideshow Management section that execute arbitrary JavaScript code on the client side, e.g., to steal the administrator's PHP session token (PHPSESSID).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40849
- https://github.com/thinkcmf/thinkcmf/issues/737
- https://github.com/thinkcmf/thinkcmf/commit/aba1f52bbf6c9515c545e046cec8416cbaefa496
- https://github.com/thinkcmf/thinkcmf/commit/b61636134aa57d4693967f35772200c779099740
- https://github.com/thinkcmf/thinkcmf
