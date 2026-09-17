# [M] Tuleap's recursive permissions to document manager folder are not properly applied

## Summary
Severity: Medium
Advisory: CVE-2024-39902
Aliases: GHSA-5jq5-vxmq-xrj7
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:H/A:N)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-39902
Type: osv

## Details
Tuleap is an open source suite to improve management of software developments and collaboration. Prior to Tuleap Community Edition 15.10.99.128 and Tuleap Enterprise Edition 15.10-6 and 15.9-8, the checkbox "Apply same permissions to all sub-items of this folder" in the document manager permissions modal is not taken into account and always considered as unchecked. In situations where the permissions are being restricted some users might still keep, incorrectly, the possibility to edit or manage items. Only change made via the web UI are affected, changes directly made via the REST API are not impacted. This vulnerability is fixed in Tuleap Community Edition 15.10.99.128 and Tuleap Enterprise Edition 15.10-6 and 15.9-8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39902.json
- https://github.com/Enalean/tuleap/commit/580161e8a065fba30ca5ca1f6f1bdb4f4b1424bb
- https://github.com/Enalean/tuleap/security/advisories/GHSA-5jq5-vxmq-xrj7
- https://nvd.nist.gov/vuln/detail/CVE-2024-39902
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=580161e8a065fba30ca5ca1f6f1bdb4f4b1424bb
- https://tuleap.net/plugins/tracker/?aid=38675
