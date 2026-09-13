# [M] Xibo CMS has Authenticated Server-Side Request Forgery (SSRF) in Remote DataSet Functionality

## Summary
Severity: Medium
Advisory: CVE-2026-31955
Aliases: GHSA-5q58-9vhx-xg2p
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31955
Type: osv

## Details
Xibo is an open source digital signage platform with a web content management system and Windows display player software. An authenticated Server-Side Request Forgery (SSRF) vulnerability in versions prior to 4.4.1 allows users with DataSet permissions to make arbitrary HTTP requests from the CMS server to internal or external network resources. This can be exploited to scan internal infrastructure, access local cloud metadata endpoints (e.g., AWS IMDS), interact with internal services that lack authentication, or exfiltrate data. Exploitation of the vulnerability is possible on behalf of an authorized user who has both of the following privileges, which are not granted to non-admins as standard: Include "Add DataSet" button to allow for additional DataSets to be created independently to Layouts. Users should upgrade to version 4.4.1 which fixes this issue. Upgrading to a fixed version is necessary to remediate. Users unable to upgrade should revoke such privileges from users they do not trust.

## References
- https://github.com/xibosignage/xibo-cms/releases/tag/4.4.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31955.json
- https://github.com/xibosignage/xibo-cms/security/advisories/GHSA-5q58-9vhx-xg2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-31955
