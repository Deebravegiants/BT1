# [H] Flowise has IDOR leading to Account Takeover and Enterprise Feature Bypass via SSO Configuration

## Summary
Severity: High
Advisory: GHSA-cwc3-p92j-g7qm
CVE: CVE-2026-30823
CWE: CWE-639, CWE-862
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-cwc3-p92j-g7qm
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.0.13

## Details
### Summary
The Flowise platform has a critical Insecure Direct Object Reference (IDOR) vulnerability combined with a Business Logic Flaw in the PUT /api/v1/loginmethod endpoint.

While the endpoint requires authentication, it fails to validate if the authenticated user has ownership or administrative rights over the target organizationId. This allows any low-privileged user (including "Free" plan users) to:

1. Overwrite the SSO configuration of any other organization.
2. Enable "Enterprise-only" features (SSO/SAML) without a license.
3. Perform Account Takeover  by redirecting the authentication flow.

### Details
The backend accepts the organizationId parameter from the JSON body and updates the database record corresponding to that ID. There is no middleware or logic check to ensure request.user.organizationId === body.organizationId.

### PoC
Prerequisites:
1. The attacker creates a standard "Free" account and obtains a valid JWT token (Cookie/Header).
2. The attacker identifies the target organizationId (e.g., bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d).

**Step-by-Step Exploitation**: The attacker sends the following PUT request to overwrite the victim's Google SSO configuration.

**Request**:

```http
PUT /api/v1/loginmethod HTTP/2
Host: cloud.flowiseai.com
Cookie: token=<ATTACKER_JWT_TOKEN>
Content-Type: application/json
Accept: application/json

{
  "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d",
  "userId": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2", 
  "providers": [
    {
      "providerLabel": "Google",
      "providerName": "google",
      "config": {
        "clientID": "ATTACKER_MALICIOUS_CLIENT_ID",
        "clientSecret": "ATTACKER_MALICIOUS_SECRET"
      },
      "status": "enable"
    }
  ]
}
```

**Response**: The server responds with 200 OK, confirming the modification has been applied to the victim's organization context.

```json
{
  "status": "OK",
  "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d"
}
```

### Impact

- **Account Takeover**: An attacker can replace a victim organization's legitimate OAuth credentials (e.g., Google Client ID) with their own malicious application credentials. When victim employees try to log in via SSO, they are authenticated against the attacker's application, potentially allowing the attacker to hijack sessions or steal credentials.
- **License Control Bypass**: Users on the "Free" tier can illicitly enable and configure SSO providers (Azure, Okta, etc.), which are features strictly restricted to the "Enterprise" plan.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-cwc3-p92j-g7qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-30823
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.13
