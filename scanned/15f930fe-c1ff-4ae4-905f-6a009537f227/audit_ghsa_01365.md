# [H] Cross-Site Scripting in atlasboard-atlassian-package

## Summary
Severity: High
Advisory: GHSA-25v4-mcx4-hh35
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-25v4-mcx4-hh35
Type: github-advisory

## Affected
- npm: `atlasboard-atlassian-package` — affected >=0.0.0

## Details
All versions of `atlasboard-atlassian-package` prior to 0.4.2 are vulnerable to Cross-Site Scripting (XSS).  The package fails to properly sanitize user input that is rendered as HTML, which may allow attackers to execute arbitrary JavaScript in a victim's browser. This requires attackers being able to change issue summaries in Jira tickets.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/456702
- https://www.npmjs.com/advisories/1449
