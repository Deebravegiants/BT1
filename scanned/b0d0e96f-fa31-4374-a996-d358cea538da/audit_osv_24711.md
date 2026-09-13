# [H] System account impersonation in DataHub

## Summary
Severity: High
Advisory: CVE-2023-25559
Aliases: GHSA-qgp2-qr66-j8r8
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-25559
Type: osv

## Details
DataHub is an open-source metadata platform. When not using authentication for the metadata service, which is the default configuration, the Metadata service (GMS) will use the X-DataHub-Actor HTTP header to infer the user the frontend is sending the request on behalf of. When the backends retrieves the header, its name is retrieved in a case-insensitive way. This case differential can be abused by an attacker to smuggle an X-DataHub-Actor header with different casing  (eg: X-DATAHUB-ACTOR). This issue may lead to an authorization bypass by allowing any user to impersonate the system user account and perform any actions on its behalf. This vulnerability was discovered and reported by the GitHub Security lab and is tracked as GHSL-2022-079.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25559.json
- https://github.com/datahub-project/datahub/security/advisories/GHSA-qgp2-qr66-j8r8
- https://nvd.nist.gov/vuln/detail/CVE-2023-25559
