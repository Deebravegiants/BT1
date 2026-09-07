# [M] Froxlor has an HTML Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-26xq-m8xw-6373
CVE: CVE-2025-48958
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-26xq-m8xw-6373
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.2.6

## Details
### Summary
_An HTML Injection vulnerability in the customer account portal allows an attacker to inject malicious HTML payloads in the email section. This can lead to phishing attacks, credential theft, and reputational damage by redirecting users to malicious external websites. The vulnerability has a medium severity, as it can be exploited through user input without authentication._

### Observation
_It is observed that in the portal of the customer account, there is a functionality in the email section to create an email address that accepts user input. By intercepting the request and modifying the "domain" field with an HTML injection payload containing an anchor tag, the injected payload is reflected on an error page. When clicked, it redirects users to an external website, confirming the presence of an HTML Injection vulnerability._

### PoC
1. Navigate to the Email section in the Customer Account Portal and create a new email address.

2. Enter any garbage value in the required field and intercept the request using Burp Suite.

3. Locate the "domain" field in the intercepted request and replace its value with the following HTML Injection payload:

	`<a href="&#x68;&#x74;&#x74;&#x70;&#x73;&#x3a;&#x2f;&#x2f;&#x77;&#x77;&#x77;&#x2e;&#x67;&#x6f;&#x6f;&#x67;&#x6c;&#x65;&#x2e;&#x63;&#x6f;&#x6d;">CLiCK</a>`

4. Forward the modified request and observe that the injected payload is reflected on an error page.

5. Click on the displayed "CLiCK" link to verify that it redirects to `https://www.google.com`, confirming the presence of HTML [Injection.]([url]([froxlor_HTML-INJECTION.mp4.zip](https://github.com/user-attachments/files/18311429/froxlor_HTML-INJECTION.mp4.zip)))

### Impact
_An attacker can exploit this HTML Injection vulnerability to manipulate the portal’s content, conduct phishing attacks, deface the application, or trick users into clicking malicious links. This can lead to credential theft, malware distribution, reputational damage, and potential compliance violations.
The users of the customer account portal are impacted by this vulnerability. Specifically, any user who interacts with the email section of the portal may be tricked into clicking malicious links, leading to potential phishing attacks, credential theft, and exposure to other malicious activities. The organization hosting the portal could also be impacted by reputational damage and compliance violations._

### Recommendation
_It is recommended to implement proper input validation and output encoding to prevent HTML Injection. The application should sanitize user input by stripping or escaping HTML tags before rendering it on the page._

## References
- https://github.com/froxlor/Froxlor/security/advisories/GHSA-26xq-m8xw-6373
- https://nvd.nist.gov/vuln/detail/CVE-2025-48958
- https://github.com/froxlor/Froxlor/commit/fde43f80600f1035e1e3d2297411b666d805549a
- https://github.com/froxlor/Froxlor
- https://github.com/user-attachments/assets/86947633-3e7c-4e10-86cc-92e577761e8e
