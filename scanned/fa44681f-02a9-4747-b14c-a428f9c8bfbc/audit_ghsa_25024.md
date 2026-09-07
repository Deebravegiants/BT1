# [M] phpMyAdmin Cross-site Scripting In MySQL Table Name

## Summary
Severity: Medium
Advisory: GHSA-5pvv-f8h3-gw96
CVE: CVE-2009-3696
CWE: CWE-79
Ecosystem: Packagist
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-5pvv-f8h3-gw96
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=2.11.0 <2.11.9.6
- Packagist: `phpmyadmin/phpmyadmin` — affected >=3.0.0 <3.2.2.1

## Details
Cross-site scripting (XSS) vulnerability in phpMyAdmin 2.11.x before 2.11.9.6 and 3.x before 3.2.2.1 allows remote attackers to inject arbitrary web script or HTML via a crafted name for a MySQL table.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2009-3696
- https://github.com/phpmyadmin/phpmyadmin/commit/212daad0c082dfb853e3a4098838781a96b2ce1f
- https://github.com/phpmyadmin/phpmyadmin/commit/8ec5434999724f61d7df1f9b0b13545274c78b1e
- https://bugzilla.redhat.com/show_bug.cgi?id=528769
- https://exchange.xforce.ibmcloud.com/vulnerabilities/53742
- https://github.com/phpmyadmin/phpmyadmin
- https://web.archive.org/web/20200228173112/http://www.securityfocus.com/bid/36658
- https://www.redhat.com/archives/fedora-package-announce/2009-October/msg00467.html
- https://www.redhat.com/archives/fedora-package-announce/2009-October/msg00490.html
- http://bugs.gentoo.org/show_bug.cgi?id=288899
- http://dfn.dl.sourceforge.net/project/phpmyadmin/phpMyAdmin/2.11.9.6/phpMyAdmin-2.11.9.6-notes.html
- http://dfn.dl.sourceforge.net/project/phpmyadmin/phpMyAdmin/3.2.2.1/phpMyAdmin-3.2.2.1-notes.html
- http://freshmeat.net/projects/phpmyadmin/releases/306667
- http://freshmeat.net/projects/phpmyadmin/releases/306669
- http://lists.opensuse.org/opensuse-security-announce/2009-10/msg00004.html
- http://marc.info/?l=oss-security&m=125553728512853&w=2
- http://marc.info/?l=oss-security&m=125561979001460&w=2
- http://typo3.org/extensions/repository/view/phpmyadmin/4.5.0
- http://typo3.org/teams/security/security-bulletins/typo3-sa-2009-015
- http://www.mandriva.com/security/advisories?name=MDVSA-2009:274
