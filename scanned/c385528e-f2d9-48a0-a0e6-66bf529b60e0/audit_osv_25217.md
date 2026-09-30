# [M] Tuleap vulnerable toXSS via the triggered job URL of a Jenkins job

## Summary
Severity: Medium
Advisory: CVE-2023-32072
Aliases: GHSA-6prc-j58r-fmjq
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-05-29
Source: https://osv.dev/vulnerability/CVE-2023-32072
Type: osv

## Details
Tuleap is an open source tool for end to end traceability of application and system developments. Tuleap Community Edition prior to version 14.8.99.60 and Tuleap Enterprise edition prior to 14.8-3 and 14.7-7, the logs of the triggered Jenkins job URLs are not properly escaped. A malicious Git administrator can setup a malicious Jenkins hook to make a victim, also a Git administrator, execute uncontrolled code. Tuleap Community Edition 14.8.99.60, Tuleap Enterprise Edition 14.8-3, and Tuleap Enterprise Edition 14.7-7 contain a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32072.json
- https://github.com/Enalean/tuleap/commit/6840529def97f564844e810e5a7c5bf837cf58d5
- https://github.com/Enalean/tuleap/security/advisories/GHSA-6prc-j58r-fmjq
- https://nvd.nist.gov/vuln/detail/CVE-2023-32072
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=6840529def97f564844e810e5a7c5bf837cf58d5
- https://tuleap.net/plugins/tracker/?aid=31929
