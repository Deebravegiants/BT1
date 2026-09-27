# [M] Mortbay Jetty Discloses JSP Source Code

## Summary
Severity: Medium
Advisory: GHSA-cwq3-qp8v-w8q3
CVE: CVE-2005-3747
CWE: CWE-200
Ecosystem: Maven
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-cwq3-qp8v-w8q3
Type: github-advisory

## Affected
- Maven: `org.mortbay.jetty:jetty` — affected >=0 <5.1.6

## Details
Unspecified vulnerability in Jetty before 5.1.6 allows remote attackers to obtain source code of JSP pages, possibly involving requests for .jsp files with URL-encoded backslash (`%5C`) characters.  NOTE: this might be the same issue as CVE-2006-2758.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2005-3747
- http://sourceforge.net/project/shownotes.php?release_id=372086&group_id=7322
- http://www.securityfocus.com/archive/1/450315/100/0/threaded
- http://www.securityfocus.com/bid/15515
