# [M] DataHub OIDC REDIRECT_URL Cookie Deserialization Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-44501
Aliases: GHSA-rjf9-p49v-42c4
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-44501
Type: osv

## Details
DataHub is an open-source metadata platform. Prior to 1.5.0.3, The DataHub frontend (datahub-frontend-react) deserializes attacker-controlled Java objects from the REDIRECT_URL HTTP cookie during the OIDC callback flow, with no integrity protection (no HMAC, no encryption). This is a Deserialization of Untrusted Data vulnerability (CWE-502) affecting the GET /callback/oidc endpoint. Successful exploitation requires a valid user account in the configured OIDC identity provider This vulnerability is fixed in 1.5.0.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44501.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-rjf9-p49v-42c4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44501
