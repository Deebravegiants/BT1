# [M] Paymenter has Blind Unauthenticated SSRF on the Paypal gateway module

## Summary
Severity: Medium
Advisory: GHSA-7wwh-xcc3-9fcg
CVE: CVE-2026-44583
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-7wwh-xcc3-9fcg
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.5.0

## Details
### Summary
The PayPal webhook endpoint `/extensions/paypal/webhook` processes the `PAYPAL-CERT-URL` HTTP header without validation, allowing attackers to control server-side HTTP request destinations.

### Technical details:

The `/extensions/paypal/webhook` endpoint processes incoming webhook requests and trusts the value of the `PAYPAL-CERT-URL` HTTP header without validation.

This value is passed directly into a server-side HTTP request via `file_get_contents`, allowing attackers to control the destination of the request. No allowlist, validation, or signature verification is applied to the header before usage.

As a result, the application can be coerced into performing HTTP requests to attacker-controlled or internal network destinations.

### Impact
This vulnerability allows remote unauthenticated attackers to induce server-side HTTP GET requests to arbitrary external or internal endpoints.

Depending on network configuration, this may lead to:

- Blind SSRF to external attacker-controlled systems
- Potential access to internal network services

No direct response data is returned to the attacker (blind SSRF), but the issue may still enable sensitive network probing or data exfiltration via side channels.

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-7wwh-xcc3-9fcg
- https://github.com/Paymenter/Paymenter
