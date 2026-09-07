# [M] Drupal vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-6cj8-c359-p7q9
CVE: CVE-2008-3218
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-6cj8-c359-p7q9
Type: github-advisory

## Affected
- Packagist: `drupal/drupal` — affected >=6.0 <6.3

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Drupal 6.x before 6.3 allow remote attackers to inject arbitrary web script or HTML via vectors related to (1) free tagging taxonomy terms, which are not properly handled on node preview pages, and (2) unspecified OpenID values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2008-3218
- https://bugzilla.redhat.com/show_bug.cgi?id=454849
- https://exchange.xforce.ibmcloud.com/vulnerabilities/43704
- https://github.com/drupal/drupal
- https://web.archive.org/web/20080804010537/http://secunia.com/advisories/31079
- https://web.archive.org/web/20081007110725/http://www.securityfocus.com/bid/30168
- https://www.redhat.com/archives/fedora-package-announce/2008-August/msg00016.html
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg00527.html
- https://www.redhat.com/archives/fedora-package-announce/2008-July/msg00551.html
- http://drupal.org/node/280571
- http://www.openwall.com/lists/oss-security/2008/07/10/3
