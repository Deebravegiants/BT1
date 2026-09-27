# [M] BIT-espocrm-2023-46736

## Summary
Severity: Medium
Advisory: BIT-espocrm-2023-46736
Aliases: CVE-2023-46736, GHSA-g955-rwxx-jvf6
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-espocrm-2023-46736
Type: osv

## Affected
- Bitnami: `espocrm` — affected >=0 <8.0.2

## Details
EspoCRM is an Open Source CRM (Customer Relationship Management) software. In affected versions there is Server-Side Request Forgery (SSRF) vulnerability via the upload image from url api. Users who have access to `the /Attachment/fromImageUrl` endpoint can specify URL to point to an internal host. Even though there is check for content type, it can be bypassed by redirects in some cases. This SSRF can be leveraged to disclose internal information (in some cases), target internal hosts and bypass firewalls. This vulnerability has been addressed in commit `c536cee63` which is included in release version 8.0.5. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/espocrm/espocrm/commit/c536cee6375e2088f961af13db7aaa652c983072
- https://github.com/espocrm/espocrm/security/advisories/GHSA-g955-rwxx-jvf6
- https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/
