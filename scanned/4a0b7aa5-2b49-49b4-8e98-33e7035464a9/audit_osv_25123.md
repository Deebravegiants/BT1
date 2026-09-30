# [M] DHIS2 Core unrestricted session cookies with Personal Access Tokens

## Summary
Severity: Medium
Advisory: CVE-2023-31139
Aliases: GHSA-44g3-9mp4-prv3
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-31139
Type: osv

## Details
DHIS2 Core contains the service layer and Web API for DHIS2, an information system for data capture. Starting in the 2.37 branch and prior to versions 2.37.9.1, 2.38.3.1, and 2.39.1.2, Personal Access Tokens (PATs) generate unrestricted session cookies. This may lead to a bypass of other access restrictions (for example, based on allowed IP addresses or HTTP methods). DHIS2 implementers should upgrade to a supported version of DHIS2: 2.37.9.1, 2.38.3.1, or 2.39.1.2. Implementers can work around this issue by adding extra access control validations on a reverse proxy.

## References
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.37/ReleaseNote-2.37.9.1.md
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.38/ReleaseNote-2.38.3.1.md
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.39/ReleaseNote-2.39.1.2.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31139.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-44g3-9mp4-prv3
- https://nvd.nist.gov/vuln/detail/CVE-2023-31139
