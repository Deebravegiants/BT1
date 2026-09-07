# [M] Open redirect vulnerability in Sourcegraph

## Summary
Severity: Medium
Advisory: GHSA-mx43-r985-5h4m
CVE: CVE-2020-12283
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-20
Source: https://github.com/advisories/GHSA-mx43-r985-5h4m
Type: github-advisory

## Affected
- Go: `github.com/sourcegraph/sourcegraph` — affected >=0 <3.14.4
- Go: `github.com/sourcegraph/sourcegraph` — affected >=3.15.0 <3.15.1

## Details
### Impact

An open redirect vulnerability that allows users to be targeted for phishing attacks has been found in Sourcegraph instances configured with OAuth, OpenID, or SAML authentication enabled. Users targeted by these phishing attacks could have their authentication tokens silently harvested by an attacker.

### Specific Go Packages Affected
github.com/sourcegraph/sourcegraph/cmd/frontend/auth

### Resolution

Sourcegraph v3.14.4 and v3.15.1 have been released which resolve the vulnerability. ([associated change](https://github.com/sourcegraph/sourcegraph/pull/10167))

### Workarounds

Disabling OAuth, OpenID and/or SAML sign-in options until upgraded to the patched versions will secure Sourcegraph / workaround the issue.

### Timeline

- Apr 23, 8 AM PST: GitHub Security Lab reported the issue to Sourcegraph.
- Apr 23, 11 PM PST: A Sourcegraph engineer proposed a resolution for the vulnerability. https://github.com/sourcegraph/sourcegraph/pull/10167
- Apr 24, 3 AM PST: The proposed resolution was reviewed, approved, and merged.
- Apr 28, 2 PM PST: Patch releases for 3.14.4 and 3.15.1 were published.
- Apr 29, 10 PM PST: Mitre publicly disclosed [CVE-2020-12283](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-12283).
- Apr 30, 11 AM PST: Sourcegraph issued a GitHub security advisory and notified all affected users.

### References

- [Mitre: CVE-2020-12283](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-12283)
- [GitHub Security Lab: GHSL-2020-085](https://securitylab.github.com/advisories/GHSL-2020-085-sourcegraph)
- [detectify's blog post on open redirect vulnerabilities
](https://blog.detectify.com/2019/05/16/the-real-impact-of-an-open-redirect/)

### For more information

If you have any questions or comments about this advisory, please contact us at [support@sourcegraph.com](mailto:support@sourcegraph.com) and include `CVE-2020-12283` in the title.

## References
- https://github.com/sourcegraph/sourcegraph/security/advisories/GHSA-mx43-r985-5h4m
- https://nvd.nist.gov/vuln/detail/CVE-2020-12283
- https://github.com/sourcegraph/sourcegraph/pull/10167
- https://github.com/sourcegraph/sourcegraph/commit/c0f48172e815c7f66471a38f0a06d1fc32a77a64
- https://github.com/sourcegraph/sourcegraph
- https://github.com/sourcegraph/sourcegraph/blob/master/CHANGELOG.md
- https://github.com/sourcegraph/sourcegraph/compare/v3.15.0...v3.15.1
- https://securitylab.github.com/advisories/GHSL-2020-085-sourcegraph
