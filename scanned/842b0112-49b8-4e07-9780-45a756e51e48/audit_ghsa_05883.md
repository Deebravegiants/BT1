# [M] Flowise: IDOR vulnerability exists at the GET /api/v1/organization/customer-default-source endpoint

## Summary
Severity: Medium
Advisory: GHSA-2364-jh4q-m9vm
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-2364-jh4q-m9vm
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
### Summary
An Insecure Direct Object Reference (IDOR) vulnerability exists at the **GET /api/v1/organization/customer-default-source** endpoint. This flaw allows an authenticated attacker to bypass authorization checks and retrieve sensitive payment and profile information of other customers by manipulating the customerId parameter. The exposed data includes email addresses, account balances, currency types, and internal billing configurations.

### Details
The application fails to implement proper object-level access control. While the endpoint requires a valid session/token, it does not verify if the requesting user has the authority to access the specific customerId provided in the query string.

When a request is made to:
GET /api/v1/organization/customer-default-source?customerId=cus_XXXX

The server processes the request based solely on the existence of a valid session, returning the data associated with the ID regardless of the data owner's identity. Since customer IDs follow a predictable pattern (Stripe-formatted cus_...), an attacker could potentially enumerate these IDs to scrape customer data.

### PoC
1. To reproduce the vulnerability, follow these steps:

2. Log in to your account at cloud.flowiseai.com.

3. Capture a request to the payment source endpoint using a proxy tool (e.g., Burp Suite).

4. Change the customerId parameter in the URL to a target user's ID (e.g., cus_U9ajkQvu0e67uH).

Execute the request:
```
GET /api/v1/organization/customer-default-source?customerId=cus_U9ajkQvu0e67uH HTTP/2
Host: cloud.flowiseai.com
Cookie: [YOUR_AUTHENTICATED_COOKIES]
...
```
Response: 
```
{
  "id": "cus_U9ajkQvu0e67uH",
  "object": "customer",
  "email": "truongnguyen210044@gmail.com",
  "balance": 0,
  "currency": "usd",
  "invoice_settings": {
    "custom_fields": null,
    "default_payment_method": null
  },
  "livemode": true
  ...
}
```
The server returns a 200 OK status with the private data of the target customer.
### Impact
- Vulnerability Type: Broken Access Control (IDOR).

- Impacted Parties: All registered users and organizations on the FlowiseAI Cloud platform.

- Consequences: * Data Privacy Breach: Exposure of Personally Identifiable Information (PII) such as email addresses.
- Financial Information Leakage: Disclosure of account balances, currency settings, and invoice metadata.

- Compliance Risk: Potential violation of data protection regulations (e.g., GDPR) due to unauthorized access to user billing profiles.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-2364-jh4q-m9vm
- https://github.com/FlowiseAI/Flowise/pull/6321
- https://github.com/FlowiseAI/Flowise/commit/4d7899d02ca370a5510406be5c91483085a412f9
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.3
