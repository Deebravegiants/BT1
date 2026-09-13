# [M] Tuleap lists trackers in the quick add actions of the backlog without any permissions check

## Summary
Severity: Medium
Advisory: CVE-2024-47767
Aliases: GHSA-j342-v27q-329v
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-14
Source: https://osv.dev/vulnerability/CVE-2024-47767
Type: osv

## Details
Tuleap is a tool for end to end traceability of application and system developments. Prior to Tuleap Community Edition 15.13.99.113, Tuleap Enterprise Edition 15.13-5, and Tuleap Enterprise Edition 15.12-5, users might see tracker names they should not have access to. Tuleap Community Edition 15.13.99.113, Tuleap Enterprise Edition 15.13-5, and Tuleap Enterprise Edition 15.12-8 fix this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47767.json
- https://github.com/Enalean/tuleap/commit/16d9efccb2fad8e10343be2604e94c9058ef2c89
- https://github.com/Enalean/tuleap/commit/e5ce81279766115dc0f126a11d6b5065b5db7eec
- https://github.com/Enalean/tuleap/commit/f89d7093d2c576ad5e2b35a6a096fcdaf563d1df
- https://github.com/Enalean/tuleap/security/advisories/GHSA-j342-v27q-329v
- https://nvd.nist.gov/vuln/detail/CVE-2024-47767
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=16d9efccb2fad8e10343be2604e94c9058ef2c89
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=e5ce81279766115dc0f126a11d6b5065b5db7eec
- https://tuleap.net/plugins/git/tuleap/tuleap/stable?a=commit&h=f89d7093d2c576ad5e2b35a6a096fcdaf563d1df
- https://tuleap.net/plugins/tracker/?aid=39728
