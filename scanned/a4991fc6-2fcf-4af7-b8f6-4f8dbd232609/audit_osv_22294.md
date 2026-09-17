# [H] SQL Injection in DHIS2's in OrgUnit program association

## Summary
Severity: High
Advisory: CVE-2022-24848
Aliases: GHSA-52vp-f7hj-cj92
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-01
Source: https://osv.dev/vulnerability/CVE-2022-24848
Type: osv

## Details
DHIS2 is an information system for data capture, management, validation, analytics and visualization. A SQL injection security vulnerability affects the `/api/programs/orgUnits?programs=` API endpoint in DHIS2 versions prior to 2.36.10.1 and 2.37.6.1. The system is vulnerable to attack only from users that are logged in to DHIS2, and there is no known way of exploiting the vulnerability without first being logged in as a DHIS2 user. The vulnerability is not exposed to a non-malicious user and requires a conscious attack to be exploited. A successful exploit of this vulnerability could allow the malicious user to read, edit and delete data in the DHIS2 instance's database. Security patches are now available for DHIS2 versions 2.36.10.1 and 2.37.6.1. One may apply mitigations at the web proxy level as a workaround. More information about these mitigations is available in the GitHub Security Advisory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24848.json
- https://github.com/dhis2/dhis2-core/security/advisories/GHSA-52vp-f7hj-cj92
- https://nvd.nist.gov/vuln/detail/CVE-2022-24848
- https://github.com/dhis2/dhis2-core/commit/3b245d04a58b78f0dc9bae8559f36ee4ca36dfac
- https://github.com/dhis2/dhis2-core/commit/ef04483a9b177d62e48dcf4e498b302a11f95e7d
- https://github.com/dhis2/dhis2-core/pull/10953
