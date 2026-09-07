# [M] Cross-site Scripting in jspwiki-war

## Summary
Severity: Medium
Advisory: GHSA-5q75-cxcq-wr26
CVE: CVE-2018-20242
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-12
Source: https://github.com/advisories/GHSA-5q75-cxcq-wr26
Type: github-advisory

## Affected
- Maven: `org.apache.jspwiki:jspwiki-war` — affected >=0 <2.11.0.M1

## Details
A carefully crafted URL could trigger an XSS vulnerability on Apache JSPWiki, from versions up to 2.10.5, which could lead to session hijacking.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20242
- https://github.com/advisories/GHSA-5q75-cxcq-wr26
- https://lists.apache.org/thread.html/8ee4644432c0a433c5c514a57d940cf6dcb0a0094acd97b36290f0b4@%3Cuser.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/aac253cfc33c0429b528e2fcbe82d3a42d742083c528f58d192dfd16@%3Ccommits.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/e42d6e93384d4a33e939989cd00ea2a06ccf1e7bb1e6bdd3bf5187c1@%3Ccommits.jspwiki.apache.org%3E
- http://www.securityfocus.com/bid/106804
