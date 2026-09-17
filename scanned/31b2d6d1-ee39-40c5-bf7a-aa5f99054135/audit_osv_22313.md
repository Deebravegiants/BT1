# [M] Tracker report renderer and chart widgets leak information in Tuleap

## Summary
Severity: Medium
Advisory: CVE-2022-24896
Aliases: GHSA-x962-x43g-qw39
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-06-06
Source: https://osv.dev/vulnerability/CVE-2022-24896
Type: osv

## Details
Tuleap is a Free & Open Source Suite to manage software developments and collaboration. In versions prior to 13.7.99.239 Tuleap does not properly verify authorizations when displaying the content of tracker report renderer and chart widgets. Malicious users could use this vulnerability to retrieve the name of a tracker they cannot access as well as the name of the fields used in reports.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24896.json
- https://github.com/Enalean/tuleap/commit/8e99e7c82d9fe569799019b9e1d614d38a184313
- https://github.com/Enalean/tuleap/security/advisories/GHSA-x962-x43g-qw39
- https://nvd.nist.gov/vuln/detail/CVE-2022-24896
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=8e99e7c82d9fe569799019b9e1d614d38a184313
- https://tuleap.net/plugins/tracker/?aid=26729
