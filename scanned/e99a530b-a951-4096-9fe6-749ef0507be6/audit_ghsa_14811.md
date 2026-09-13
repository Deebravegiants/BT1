# [M] Sensitive Data Disclosure Vulnerability in Connection Configuration Endpoints

## Summary
Severity: Medium
Advisory: GHSA-rcvg-jj3g-rj7c
CVE: CVE-2024-35189
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-rcvg-jj3g-rj7c
Type: github-advisory

## Affected
- PyPI: `ethyca-fides` — affected >=0 <2.37.0

## Details
The Fides webserver has a number of endpoints that retrieve `ConnectionConfiguration` records and their associated `secrets` which _can_ contain sensitive data (e.g. passwords, private keys, etc.). These `secrets` are stored encrypted at rest (in the application database), and the associated endpoints are not meant to expose that sensitive data in plaintext to API clients, as it could be compromising. 

Fides's developers have available to them a Pydantic field-attribute (`sensitive`) that they can annotate as `True` to indicate that a given secret field should not be exposed via the API. The application has an internal function that uses `sensitive` annotations to mask the sensitive fields with a `"**********"` placeholder value.

This vulnerability is due to a bug in that function, which prevented `sensitive` API model fields that were _nested_ below the root-level of a `secrets` object from being masked appropriately. Only the `BigQuery` connection configuration secrets meets these criteria: the secrets schema has a nested sensitive `keyfile_creds.private_key` property that is exposed in plaintext via the APIs.

Connection types other than `BigQuery` with sensitive fields at the root-level that are not nested are properly masked with the placeholder and are not affected by this vulnerability.


### Impact

The Google Cloud secrets used for a Fides BigQuery integration may be retrieved in plaintext by any authenticated Admin UI user, except those with the Approver role. Any API users authorized to access the following endpoints may also retrieve the key in plaintext.

Endpoints impacted:
- `GET /api/v1/connections`
- `PATCH /api/v1/connections`
- `GET /api/v1/connection/{connection_key}`
- `PATCH /api/v1/system/{system_key}/connection`
- `GET /api/v1/system/{system_key}`
- `GET /api/v1/system/{system_key}/connection`

Connection config secret schemas impacted:
- `BigQuerySchema`

### Patches
The vulnerability has been patched in Fides version `2.37.0`. Users are advised to upgrade to this version or later to secure their systems against this threat.

Users are also advised to rotate any Google Cloud secrets used for BigQuery integrations in their Fides deployments: https://cloud.google.com/iam/docs/key-rotation

### Workarounds
There are no workarounds.

### Proof of concept

Multiple endpoints are impacted, but this PoC will use `GET /api/v1/system/{system_key}` as an example.

1. Using the Admin UI, navigate to `/add-systems`. Add and save a new system `bq_poc`.
2. In the integrations tab of the new system, configure and save a BigQuery integration with secrets.
3. Log in as a different user with any role except Approver and navigate to the `/systems` page.
4. Open the network section of your browser's developer tools.
5. Click on the `bq_poc` system's meatball menu and then click edit.
6. In the network section of browser dev tools you will observe a HTTP GET http://localhost:8080/api/v1/system/bq_poc/ request. In the body of the JSON response the integration secrets values entered in Step 2 are exposed in plaintext i.e.

```json
{
  "secrets": {
    "keyfile_creds": {
      "type": "value",
      "project_id": "value",
      "private_key_id": "value",
      "private_key": "value",
      "client_email": "value",
      "client_id": "value",
      "auth_uri": "value",
      "token_uri": "value",
      "auth_provider_x509_cert_url": "value",
      "client_x509_cert_url": "value"
    }
  }
}
```

## References
- https://github.com/ethyca/fides/security/advisories/GHSA-rcvg-jj3g-rj7c
- https://nvd.nist.gov/vuln/detail/CVE-2024-35189
- https://cloud.google.com/iam/docs/key-rotation
- https://github.com/ethyca/fides
