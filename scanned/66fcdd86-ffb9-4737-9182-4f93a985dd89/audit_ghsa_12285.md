# [M] Root Path Disclosure in send

## Summary
Severity: Medium
Advisory: GHSA-jgqf-hwc5-hh37
CVE: CVE-2015-8859
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-jgqf-hwc5-hh37
Type: github-advisory

## Affected
- npm: `send` — affected >=0 <0.11.1

## Details
Versions of `send` prior to 0.11.2 are affected by an information leakage vulnerability which may allow an attacker to enumerate paths on the server filesystem.



## Recommendation

Update to version 0.11.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8859
- https://github.com/pillarjs/send/pull/70
- https://github.com/pillarjs/send/commit/98a5b89982b38e79db684177cf94730ce7fc7aed
- https://github.com/expressjs/serve-static/blob/master/HISTORY.md#181--2015-01-20
- https://github.com/pillarjs/send
- https://web.archive.org/web/20200227192016/https://www.securityfocus.com/bid/96435
- http://www.openwall.com/lists/oss-security/2016/04/20/11
