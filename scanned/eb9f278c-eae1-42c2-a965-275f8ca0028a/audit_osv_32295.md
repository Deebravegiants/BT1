# [M] Tuleap allows content injection via emails sent by the mass emailing features

## Summary
Severity: Medium
Advisory: CVE-2025-27156
Aliases: GHSA-x2v2-xr59-c9cf
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-27156
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. The mass emailing features do not sanitize the content of the HTML emails. A malicious user could use this issue to facilitate a phishing attempt or to indirectly exploit issues in the recipients mail clients. This vulnerability is fixed in Tuleap Community Edition 16.4.99.1740567344 and Tuleap Enterprise Edition 16.4-6 and 16.3-11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27156.json
- https://github.com/Enalean/tuleap/commit/a0bc657297b405debce1f5bcbbb30c733f3f09bd
- https://github.com/Enalean/tuleap/security/advisories/GHSA-x2v2-xr59-c9cf
- https://nvd.nist.gov/vuln/detail/CVE-2025-27156
- https://tuleap.net/plugins/tracker/?aid=42177
