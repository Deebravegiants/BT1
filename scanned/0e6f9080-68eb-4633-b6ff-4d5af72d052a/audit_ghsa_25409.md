# [H] Django vulnerable to Denial of Service via i18n middleware component

## Summary
Severity: High
Advisory: GHSA-9v8h-57gv-qch6
CVE: CVE-2007-5712
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-9v8h-57gv-qch6
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0.96.0 <0.96.1
- PyPI: `Django` — affected >=0.95 <0.95.2
- PyPI: `Django` — affected >=0.91.0 <0.91.1

## Details
The internationalization (i18n) framework in Django 0.91, 0.95, 0.95.1, and 0.96, and as used in other products such as PyLucid, when the USE_I18N option and the i18n component are enabled, allows remote attackers to cause a denial of service (memory consumption) via many HTTP requests with large Accept-Language headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-5712
- https://github.com/django/django/commit/412ed22502e11c50dbfee854627594f0e7e2c234
- https://github.com/django/django/commit/7dd2dd08a79e388732ce00e2b5514f15bd6d0f6f
- https://github.com/django/django/commit/8bc36e726c9e8c75c681d3ad232df8e882aaac81
- https://exchange.xforce.ibmcloud.com/vulnerabilities/38143
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2007-1.yaml
- https://web.archive.org/web/20091201070224/http://secunia.com/advisories/27435
- https://web.archive.org/web/20111224195100/http://secunia.com/advisories/27597
- https://web.archive.org/web/20111229085535/http://secunia.com/advisories/31961
- https://web.archive.org/web/20200228183657/http://www.securityfocus.com/bid/26227
- https://www.redhat.com/archives/fedora-package-announce/2007-November/msg00243.html
- https://www.redhat.com/archives/fedora-package-announce/2007-November/msg00257.html
- http://sourceforge.net/forum/forum.php?forum_id=749199
- http://www.debian.org/security/2008/dsa-1640
- http://www.djangoproject.com/weblog/2007/oct/26/security-fix
