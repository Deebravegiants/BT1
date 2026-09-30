# [C] ReviewBoard and Djblets library are vulnerable to code execution

## Summary
Severity: Critical
Advisory: GHSA-58h8-44mg-r43x
CVE: CVE-2013-4409
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-58h8-44mg-r43x
Type: github-advisory

## Affected
- PyPI: `djblets` — affected >=0 <0.6.30
- PyPI: `djblets` — affected >=0.7.0 <0.7.19
- PyPI: `ReviewBoard` — affected >=0 <1.7.15

## Details
An eval() vulnerability exists in Python Software Foundation Djblets version before 0.6.30 and 0.7.0 before 0.7.19 and Beanbag Review Board before 1.7.15 when parsing JSON requests allowing an attacker to execute arbitrary Python code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4409
- https://access.redhat.com/security/cve/cve-2013-4409
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-4409
- https://exchange.xforce.ibmcloud.com/vulnerabilities/88059
- https://github.com/djblets/djblets
- https://github.com/djblets/djblets/blob/release-0.7.19/NEWS
- https://github.com/pypa/advisory-database/tree/main/vulns/djblets/PYSEC-2019-175.yaml
- https://security-tracker.debian.org/tracker/CVE-2013-4409
- https://web.archive.org/web/20200228151135/https://www.securityfocus.com/bid/63029
- https://www.reviewboard.org/docs/releasenotes/reviewboard/1.7.15
- http://lists.fedoraproject.org/pipermail/package-announce/2013-November/120619.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-October/119819.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-October/119820.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-October/119830.html
- http://lists.fedoraproject.org/pipermail/package-announce/2013-October/119831.html
