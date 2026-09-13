# [M] Tuleap's mass update clears the permissions on artifact field

## Summary
Severity: Medium
Advisory: CVE-2024-25130
Aliases: GHSA-mq7f-m6mj-hjj5
CVSS: 5.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2024-25130
Type: osv

## Details
Tuleap is an open source suite to improve management of software developments and collaboration. Prior to version 15.5.99.76 of Tuleap Community Edition and prior to versions 15.5-4 and 15.4-7 of Tuleap Enterprise Edition, users with a read access to a tracker where the mass update feature is used might get access to restricted information. Tuleap Community Edition 15.5.99.76, Tuleap Enterprise Edition 15.5-4, and Tuleap Enterprise Edition 15.4-7 contain a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25130.json
- https://github.com/Enalean/tuleap/commit/57978a32508f5c6d0365419b6eaeb368aee20667
- https://github.com/Enalean/tuleap/security/advisories/GHSA-mq7f-m6mj-hjj5
- https://nvd.nist.gov/vuln/detail/CVE-2024-25130
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=57978a32508f5c6d0365419b6eaeb368aee20667
- https://tuleap.net/plugins/tracker/?aid=36803
