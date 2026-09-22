# [H] DHIS2 Core vulnerable to Improper Access Control with PATCH requests

## Summary
Severity: High
Advisory: CVE-2023-31138
Aliases: GHSA-pwvw-4m67-f4g2
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2023-05-09
Source: https://osv.dev/vulnerability/CVE-2023-31138
Type: osv

## Details
DHIS2 Core contains the service layer and Web API for DHIS2, an information system for data capture. Starting in the 2.36 branch and prior to versions 2.37.9.1, 2.38.3.1, and 2.39.1.2, using object model traversal in the payload of a PATCH request, authenticated users with write access to an object may be able to modify related objects that they should not have access to. DHIS2 implementers should upgrade to a supported version of DHIS2 to receive a patch: 2.37.9.1, 2.38.3.1, or 2.39.1.2. It is possible to work around this issue by blocking all PATCH requests on a reverse proxy, but this may cause some issues with the functionality of built-in applications using legacy PATCH requests.

## References
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.37/ReleaseNote-2.37.9.1.md
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.38/ReleaseNote-2.38.3.1.md
- https://github.com/dhis2/dhis2-releases/blob/master/releases/2.39/ReleaseNote-2.39.1.2.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31138.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-pwvw-4m67-f4g2
- https://nvd.nist.gov/vuln/detail/CVE-2023-31138
