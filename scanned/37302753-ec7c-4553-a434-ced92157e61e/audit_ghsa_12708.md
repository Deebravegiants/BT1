# [H] Jenkins CSRF protection bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-98fp-r22g-wpj7
CVE: CVE-2023-35141
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-98fp-r22g-wpj7
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.400

## Details
Jenkins provides context menus for various UI elements, like links to jobs and builds, or breadcrumbs.

In Jenkins 2.399 and earlier, LTS 2.387.3 and earlier, POST requests are sent in order to load the list of context actions. If part of the URL includes insufficiently escaped user-provided values, a victim may be tricked into sending a POST request to an unexpected endpoint (e.g., the Script Console) by opening a context menu.

As of publication of this advisory, we are aware of insufficiently escaped context menu URLs for label expressions, allowing attackers with Item/Configure permissions to exploit this vulnerability.

Jenkins 2.400, LTS 2.401.1 sends GET requests to load the list of context actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35141
- https://github.com/CVEProject/cvelist/blob/f37e157216b8e5e64a6db80b7b68bde0088277fe/2023/35xxx/CVE-2023-35141
- https://www.jenkins.io/security/advisory/2023-06-14/#SECURITY-3135
- http://www.openwall.com/lists/oss-security/2023/06/14/5
