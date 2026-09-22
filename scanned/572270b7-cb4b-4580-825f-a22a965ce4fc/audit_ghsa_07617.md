# [H] Leaky JWTs in OpenMetadata exposing highly-privileged bot users

## Summary
Severity: High
Advisory: GHSA-pqqf-7hxm-rj5r
CVE: CVE-2026-26010
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-pqqf-7hxm-rj5r
Type: github-advisory

## Affected
- Maven: `org.open-metadata:openmetadata-sdk` — affected >=0 <1.11.8

## Details
### Summary
Calls issued by the UI against `/api/v1/ingestionPipelines` leak JWTs used by `ingestion-bot` for certain services (Glue / Redshift / Postgres)

### Details
Any read-only user can gain access to a highly privileged account, typically which has the Ingestion Bot Role. This enables destructive changes in OpenMetadata instances, and potential data leakage (e.g. sample data, or service metadata which would be unavailable per roles/policies). 


### PoC
I was able to extract the JWT used by the bot/agent populating [sample_athena.default](https://sandbox.open-metadata.org/database/sample_athena.default) in the Collate Sandbox. To prove this out, I mutated the description to this UUID: `fe2e4cc1-da72-4acf-8535-112a3cfa9c7e,` which you can see  @ https://sandbox.open-metadata.org/database/sample_athena.default.

#### Steps to Reproduce

* Create a Collate Sandbox account; these are non-admin accounts by default with minimal permissions.
* Open the Developer Console
* Go to the Services Page. In this case, [sample_athena](https://sandbox.open-metadata.org/service/databaseServices/sample_athena?showDeletedTables=false&currentPage=1), though other services 
* In the Network tab, introspect the request made to api/v1/services/ingestionPipelines, and find the jwtToken in the response:
<img width="1329" height="299" alt="image" src="https://github.com/user-attachments/assets/0c405776-159e-4188-9591-ed8cc71bc596" />

* Use the JWT to issue (potentially destructive) API calls
<img width="3024" height="1798" alt="image" src="https://github.com/user-attachments/assets/ab40b528-4d2b-404b-8f8a-482a1693e179" />

* Resulting mutated description:
<img width="622" height="399" alt="image" src="https://github.com/user-attachments/assets/3fa630ff-93b5-4b7d-8e3c-220f8a84a23a" />

Note that this is also the case for these services, among others:
* [acme_nexus_redshift](https://sandbox.open-metadata.org/service/databaseServices/acme_nexus_redshift) 
* [sample_postgres](https://sandbox.open-metadata.org/service/databaseServices/sample_postgres)

### Proposed Remediation
Redact jwtToken in API payload.
Implement role-based filtering - Only return JWT tokens to users with explicit admin/service account permissions
(for Admins) Rotate Ingestion Bot Tokens in affected environments

### Impact
_What kind of vulnerability is it? Who is impacted?_

* Vulnerability Type: Privilege Escalation
* Risk: User impersonation, even for those with read-only access, can lead to destructive outcomes if malicious actors leverage the leaked JWT.

## References
- https://github.com/open-metadata/OpenMetadata/security/advisories/GHSA-pqqf-7hxm-rj5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26010
- https://github.com/open-metadata/OpenMetadata
- https://github.com/open-metadata/OpenMetadata/releases/tag/1.11.8-release
