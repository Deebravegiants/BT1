# [M] CVE-2019-0224

## Summary
Severity: Medium
Advisory: CVE-2019-0224
Aliases: GHSA-fmpq-w5q6-9vf9
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-03-28
Source: https://osv.dev/vulnerability/CVE-2019-0224
Type: osv

## Details
In Apache JSPWiki 2.9.0 to 2.11.0.M2, a carefully crafted URL could execute javascript on another user's session. No information could be saved on the server or jspwiki database, nor would an attacker be able to execute js on someone else's browser; only on its own browser.

## References
- https://lists.apache.org/thread.html/aac253cfc33c0429b528e2fcbe82d3a42d742083c528f58d192dfd16%40%3Ccommits.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/b4b4992a93d899050c1117a07c3c7fc9a175ec0672ab97065228de67%40%3Cdev.jspwiki.apache.org%3E
- https://lists.apache.org/thread.html/e42d6e93384d4a33e939989cd00ea2a06ccf1e7bb1e6bdd3bf5187c1%40%3Ccommits.jspwiki.apache.org%3E
- http://www.securityfocus.com/bid/107631
- https://jspwiki-wiki.apache.org/Wiki.jsp?page=CVE-2019-0224
