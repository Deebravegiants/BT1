# [C] XWiki Platform CSRF remote code execution through scheduler job's document reference

## Summary
Severity: Critical
Advisory: GHSA-37m4-hqxv-w26g
CVE: CVE-2024-31986
CWE: CWE-352, CWE-95
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-37m4-hqxv-w26g
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=3.1 <14.10.19
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=15.0-rc-1 <15.5.4
- Maven: `org.xwiki.platform:xwiki-platform-scheduler-ui` — affected >=15.6-rc-1 <15.9

## Details
### Impact
By creating a document with a special crafted documented reference and an `XWiki.SchedulerJobClass` XObject, it is possible to execute arbitrary code on the server whenever an admin visits the scheduler page or the scheduler page is referenced, e.g., via an image in a comment on a page in the wiki.

To reproduce on an XWiki installation, click on this link to create a new document : `<xwiki-host>/xwiki/bin/view/%22%3E%5D%5D%7B%7B%2Fhtml%7D%7D%7B%7Basync%20context%3D%22request/parameters%22%7D%7D%7B%7Bvelocity%7D%7D%23evaluate%28%24request/eval%29/`.
Then, add to this document an object of type `XWiki.SchedulerJobClass`.
Finally, as an admin, go to  `<xwiki-host>/xwiki/bin/view/Scheduler/?eval=$services.logging.getLogger(%22attacker%22).error(%22Hello%20from%20URL%20Parameter!%20I%20got%20programming:%20$services.security.authorization.hasAccess(%27programming%27)%22)`.
If the logs contain `ERROR attacker - Hello from URL Parameter! I got programming: true`, the installation is vulnerable.

### Patches
The vulnerability has been fixed on XWiki 14.10.19, 15.5.5, and 15.9.

### Workarounds
Modify the Scheduler.WebHome page following this [patch](https://github.com/xwiki/xwiki-platform/commit/f16ca4ef1513f84ce2e685d4a05d689bd3a2ab4c#diff-1e2995eacccbbbdcc4987ff64f46ac74837d166cf9e92920b4a4f8af0f10bd47).

### References
- https://jira.xwiki.org/browse/XWIKI-21416
- https://github.com/xwiki/xwiki-platform/commit/f16ca4ef1513f84ce2e685d4a05d689bd3a2ab4c

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-37m4-hqxv-w26g
- https://nvd.nist.gov/vuln/detail/CVE-2024-31986
- https://github.com/xwiki/xwiki-platform/commit/8a92cb4bef7e5f244ae81eed3e64fe9be95827cf
- https://github.com/xwiki/xwiki-platform/commit/efd3570f3e5e944ec0ad0899bf799bf9563aef87
- https://github.com/xwiki/xwiki-platform/commit/f30d9c641750a3f034b5910c6a3a7724ae8f2269
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-21416
