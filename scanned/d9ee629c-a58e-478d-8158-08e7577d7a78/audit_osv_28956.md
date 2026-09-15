# [M] bbb-web API additional parameters considered

## Summary
Severity: Medium
Advisory: CVE-2024-38518
Aliases: GHSA-4m48-49h7-f3c4
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:L)
Published: 2024-06-28
Source: https://osv.dev/vulnerability/CVE-2024-38518
Type: osv

## Details
BigBlueButton is an open-source virtual classroom designed to help teachers teach and learners learn. An attacker with a valid join link to a meeting can trick BigBlueButton into generating a signed join link with additional parameters. One of those parameters may be "role=moderator", allowing an attacker to join a meeting as moderator using a join link that was originally created for viewer access. This vulnerability has been patched in version(s) 2.6.18, 2.7.8 and 3.0.0-alpha.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38518.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-4m48-49h7-f3c4
- https://nvd.nist.gov/vuln/detail/CVE-2024-38518
- https://github.com/bigbluebutton/bigbluebutton/commit/a9d436accdcd26ea66bed9f391488ac128cd62d1
- https://github.com/bigbluebutton/bigbluebutton/commit/ea6e9461dceae8fa593543d8c686f77bb8677e72
- https://github.com/bigbluebutton/bigbluebutton/pull/20279
