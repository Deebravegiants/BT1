# [M] Renovate vulnerable to leakage of temporary repository tokens into Pull Request comments

## Summary
Severity: Medium
Advisory: GHSA-v7x3-7hw7-pcjg
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2019-10-21
Source: https://github.com/advisories/GHSA-v7x3-7hw7-pcjg
Type: github-advisory

## Affected
- npm: `renovate` — affected >=13.87.0 <19.38.7

## Details
### Impact

Temporary repository tokens were leaked into Pull Requests comments in during certain Go Modules update failure scenarios.

### Patches

The problem has been patched. Self-hosted users should upgrade to v19.38.7 or later.

### Workarounds

Disable Go Modules support.

### References

Blog post: https://renovatebot.com/blog/go-modules-vulnerability-disclosure

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Renovate](http://github.com/renovatebot/renovate)

## References
- https://github.com/renovatebot/renovate/security/advisories/GHSA-v7x3-7hw7-pcjg
- https://github.com/advisories/GHSA-v7x3-7hw7-pcjg
- https://github.com/renovatebot/renovate
- https://snyk.io/vuln/SNYK-JS-RENOVATE-536203
