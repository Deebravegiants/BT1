# [M] Tuleap's content of artifacts might be readable by unauthorized users

## Summary
Severity: Medium
Advisory: CVE-2024-23344
Aliases: GHSA-m3v5-2j5q-x85w
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-23344
Type: osv

## Details
Tuleap is an Open Source Suite to improve management of software developments and collaboration. Some users might get access to restricted information when a process validates the permissions of multiple users (e.g. mail notifications). This issue has been patched in version 15.4.99.140 of Tuleap Community Edition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23344.json
- https://github.com/Enalean/tuleap/commit/0329e21d268510bc00fed707406103edabf10e42
- https://github.com/Enalean/tuleap/security/advisories/GHSA-m3v5-2j5q-x85w
- https://nvd.nist.gov/vuln/detail/CVE-2024-23344
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=0329e21d268510bc00fed707406103edabf10e42
- https://tuleap.net/plugins/tracker/?aid=35862
