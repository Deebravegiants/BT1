# [M] Authenticated OpenRedirect Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r3qr-vwvg-43f7
CVE: CVE-2022-41965
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-11-30
Source: https://github.com/advisories/GHSA-r3qr-vwvg-43f7
Type: github-advisory

## Affected
- Maven: `org.opencastproject:opencast-common` — affected >=0 <12.5

## Details
**Description**
Prior to Opencast 12.5 Opencast's Paella authentication page could be used to redirect to an arbitrary URL for authenticated users.

**Impact**
The vulnerability allows attackers to redirect users to sites outside of your Opencast install, potentially facilitating phishing attacks or other security issues.

**Patches**
This issue is fixed in Opencast 12.5 and newer

**References**
[Patch fixing the issue](https://github.com/opencast/opencast/commit/d2ce2321590f86b066a67e8c231cf68219aea017)

**If you have any questions or comments about this advisory**:
Open an issue in [our issue tracker](https://github.com/opencast/opencast/issues)
Email us at [security@opencast.org](mailto:security@opencast.org)

## References
- https://github.com/opencast/opencast/security/advisories/GHSA-r3qr-vwvg-43f7
- https://nvd.nist.gov/vuln/detail/CVE-2022-41965
- https://github.com/opencast/opencast/commit/d2ce2321590f86b066a67e8c231cf68219aea017
- https://github.com/opencast/opencast
