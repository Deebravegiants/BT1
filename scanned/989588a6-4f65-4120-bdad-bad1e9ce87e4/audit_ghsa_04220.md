# [M] Paymenter has broken object level authorization via service reference manipulation on ticket creation

## Summary
Severity: Medium
Advisory: GHSA-x93q-x9pc-w5hw
CVE: CVE-2026-44585
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-x93q-x9pc-w5hw
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.5.0

## Details
### Summary
The ticket creation endpoint accepts a user-supplied service identifier without enforcing ownership validation, allowing authenticated users to create support tickets referencing services belonging to other accounts by modifying the service ID in the request.

### Technical Details

The ticket creation endpoint accepted a user-supplied service identifier without verifying ownership or authorization against the authenticated account. An attacker could modify the service ID value in the client-side request and successfully create a ticket associated with another user's service.

The vulnerability required authentication and did not provide direct access to service contents or customer data. However, referenced service information could become visible to support personnel handling the ticket.

### Impact

Successful exploitation could allow an authenticated user to:
- Create support tickets referencing services belonging to other users
- Potentially cause support staff to interact with or review unrelated customer services

The vulnerability did not allow:
- Direct access to another user's service
- Modification of another user's service
- Retrieval of confidential service data through the vulnerable endpoint itself

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-x93q-x9pc-w5hw
- https://github.com/Paymenter/Paymenter
