# [H] Improper Limitation of a Pathname ('Path Traversal')  in org.apache.jspwiki:jspwiki-war

## Summary
Severity: High
Advisory: GHSA-pffw-p2q5-w6vh
CVE: CVE-2019-0225
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-04-08
Source: https://github.com/advisories/GHSA-pffw-p2q5-w6vh
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-war` — affected >=2.9.0 <2.11.0.M3

## Details
A specially crafted url could be used to access files under the ROOT directory of the application on Apache JSPWiki 2.9.0 to 2.11.0.M2, which could be used by an attacker to obtain registered users' details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0225
- https://github.com/advisories/GHSA-pffw-p2q5-w6vh
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2019-0225
- https://lists.apache.org/thread.html/03ddbcb1d6322e04734e65805a147a32bcfdb71b8fc5821fb046ba8d@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/4f19fdbd8b9c4caf6137a459d723f4ec60379b033ed69277eb4e0af9@%3Cuser.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/6251c06cb11e0b495066be73856592dbd7ed712487ef283d10972831@%3Cdev.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/aac253cfc33c0429b528e2fcbe82d3a42d742083c528f58d192dfd16@%3Ccommits.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/e42d6e93384d4a33e939989cd00ea2a06ccf1e7bb1e6bdd3bf5187c1@%3Ccommits.jspwiki.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/03/26/2
- http://www.securityfocus.com/bid/107627
