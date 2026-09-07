# [M] XSS due to lack of CSRF validation for replying/publishing

## Summary
Severity: Medium
Advisory: GHSA-43m5-c88r-cjvv
CVE: CVE-2020-15156
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-08-26
Source: https://github.com/advisories/GHSA-43m5-c88r-cjvv
Type: github-advisory

## Affected
- npm: `nodebb-plugin-blog-comments` — affected >=0 <0.7.0

## Details
### Impact
Due to lack of CSRF validation, a logged in user is potentially vulnerable to an XSS attack which could allow a third party to post on their behalf on the forum.

### Patches
Upgrade to the latest version v0.7.0

### Workarounds
You can cherry-pick the following commit: [https://github.com/psychobunny/nodebb-plugin-blog-comments/commit/cf43beedb05131937ef46f365ab0a0c6fa6ac618](https://github.com/psychobunny/nodebb-plugin-blog-comments/commit/cf43beedb05131937ef46f365ab0a0c6fa6ac618)

### References
Visit https://community.nodebb.org if you have any questions about this issue or on how to patch / upgrade your instance.

## References
- https://github.com/psychobunny/nodebb-plugin-blog-comments/security/advisories/GHSA-43m5-c88r-cjvv
- https://nvd.nist.gov/vuln/detail/CVE-2020-15156
- https://github.com/psychobunny/nodebb-plugin-blog-comments/commit/cf43beedb05131937ef46f365ab0a0c6fa6ac618
- https://www.npmjs.com/package/nodebb-plugin-blog-comments
