# [M] Wire UI has a JS XSS Vulnerability on route /wireui/button?label=Content

## Summary
Severity: Medium
Advisory: GHSA-rw5h-g8xq-6877
CVE: CVE-2024-45803
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-rw5h-g8xq-6877
Type: github-advisory

## Affected
- Packagist: `wireui/wireui` — affected >=0 <1.19.3
- Packagist: `wireui/wireui` — affected >=2.0.0 <2.1.3

## Details
### Summary
A potential Cross-Site Scripting (XSS) vulnerability has been identified in the `/wireui/button` endpoint, specifically through the `label` query parameter. Malicious actors could exploit this vulnerability by injecting JavaScript into the `label` parameter, leading to the execution of arbitrary code in the victim's browser.

### Details
The `/wireui/button` endpoint dynamically renders button labels based on user-provided input via the `label` query parameter. Due to insufficient sanitization or escaping of this input, an attacker can inject malicious JavaScript. The following URL demonstrates the vulnerability:

```
https://wireui.dev/wireui/button?label=Cancel&1%25%7ds8dk0%3E%3Cscript%3Ealert(1)%3C/script%3Ez1qt3=1
```

By crafting such a request, an attacker can inject arbitrary code that will be executed by the browser when the endpoint is accessed.

### Proof of Concept (PoC)
To demonstrate the vulnerability, visit the following URL:

```
/wireui/button?label=<script>alert(1)</script>
```

Upon loading the page, the injected JavaScript will execute, displaying an alert with the message "1." This confirms the vulnerability and highlights that user input is not being properly escaped or sanitized.

### Impact
If exploited, this vulnerability could allow an attacker to execute arbitrary JavaScript code in the context of the affected website. This could lead to:

- **Session Hijacking**: Stealing session cookies, tokens, or other sensitive information.
- **User Impersonation**: Performing unauthorized actions on behalf of authenticated users.
- **Phishing**: Redirecting users to malicious websites.
- **Content Manipulation**: Altering the appearance or behavior of the affected page to mislead users or execute further attacks.

The severity of this vulnerability depends on the context of where the affected component is used, but in all cases, it poses a significant risk to user security.

## References
- https://github.com/wireui/wireui/security/advisories/GHSA-rw5h-g8xq-6877
- https://nvd.nist.gov/vuln/detail/CVE-2024-45803
- https://github.com/wireui/wireui/commit/784c4f110e58eb41d0f2bdecd4655ea417f16e7e
- https://github.com/wireui/wireui/commit/a457654912055f4dcc559da04d4e319f76b80fc5
- https://github.com/wireui/wireui
