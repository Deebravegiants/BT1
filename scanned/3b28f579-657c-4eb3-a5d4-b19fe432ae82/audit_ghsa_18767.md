# [M] bagisto has Server Side Template Injection (SSTI) in Product Description

## Summary
Severity: Medium
Advisory: GHSA-527q-4wqv-g9wj
CVE: CVE-2025-62416
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-10-16
Source: https://github.com/advisories/GHSA-527q-4wqv-g9wj
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.8

## Details
### Summary
Bagisto v2.3.7 is vulnerable to Server-Side Template Injection (SSTI) due to unsanitized user input being processed by the server-side templating engine when rendering product descriptions. This allows an attacker with product creation privileges to inject arbitrary template expressions that are evaluated by the backend — potentially leading to Remote Code Execution (RCE) on the server.

### Details
In Bagisto, product descriptions are rendered through Laravel’s Blade templating engine in various front-end and admin views. The product description field is not sanitized or escaped before being passed to the view, which means user-supplied data can break out of the expected string context and execute arbitrary template code.

### PoC
Create a product and enter the payload to the description.
<img width="679" height="669" alt="image" src="https://github.com/user-attachments/assets/1e5dac3f-4043-4b31-98ed-f4346feb5477" />
Preview the page, observed that the template expressions were evaluated by the backend and displayed on the screen.
<img width="1431" height="922" alt="image" src="https://github.com/user-attachments/assets/16f29c6e-05f4-40c4-9926-0c59e0a979c2" />


### Impact
RCE potential: Attackers can execute arbitrary PHP code or system commands.
Data breach: Read sensitive environment variables (.env), API keys, or database credentials.
Defacement / persistence: Inject malicious scripts or backdoors in dynamic templates.
Privilege escalation: If attackers have limited roles (e.g., product manager), they can compromise the entire application or host.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-527q-4wqv-g9wj
- https://nvd.nist.gov/vuln/detail/CVE-2025-62416
- https://github.com/bagisto/bagisto
