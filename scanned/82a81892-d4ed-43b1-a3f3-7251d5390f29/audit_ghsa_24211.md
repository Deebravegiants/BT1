# [M] Django XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pw27-w7w4-9qc7
CVE: CVE-2016-2512
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-pw27-w7w4-9qc7
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.8.10
- PyPI: `Django` — affected >=1.9a1 <1.9.3

## Details
The `utils.http.is_safe_url function` in Django before 1.8.10 and 1.9.x before 1.9.3 allows remote attackers to redirect users to arbitrary web sites and conduct phishing attacks or possibly conduct cross-site scripting (XSS) attacks via a URL containing basic authentication, as demonstrated by `http://mysite.example.com\@attacker.com`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2512
- https://github.com/django/django/commit/382ab137312961ad62feb8109d70a5a581fe8350
- https://github.com/django/django/commit/c5544d289233f501917e25970c03ed444abbd4f0
- https://github.com/django/django/commit/fc6d147a63f89795dbcdecb0559256470fff4380
- https://github.com/django/django
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2016-15.yaml
- https://web.archive.org/web/20210123090815/http://www.securityfocus.com/bid/83879
- https://web.archive.org/web/20210413200202/http://www.securitytracker.com/id/1035152
- https://www.djangoproject.com/weblog/2016/mar/01/security-releases
- http://rhn.redhat.com/errata/RHSA-2016-0502.html
- http://rhn.redhat.com/errata/RHSA-2016-0504.html
- http://rhn.redhat.com/errata/RHSA-2016-0505.html
- http://rhn.redhat.com/errata/RHSA-2016-0506.html
- http://www.debian.org/security/2016/dsa-3544
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.ubuntu.com/usn/USN-2915-1
- http://www.ubuntu.com/usn/USN-2915-2
- http://www.ubuntu.com/usn/USN-2915-3
