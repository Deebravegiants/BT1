# [C] Django Potential account hijack via password reset form

## Summary
Severity: Critical
Advisory: GHSA-vfq6-hq5r-27r6
CVE: CVE-2019-19844
CWE: CWE-640
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-16
Source: https://github.com/advisories/GHSA-vfq6-hq5r-27r6
Type: github-advisory

## Affected
- PyPI: `Django` — affected >=0 <1.11.27
- PyPI: `Django` — affected >=2.0 <2.2.9
- PyPI: `Django` — affected >=3.0 <3.0.1

## Details
Django before 1.11.27, 2.x before 2.2.9, and 3.x before 3.0.1 allows account takeover. A suitably crafted email address (that is equal to an existing user's email address after case transformation of Unicode characters) would allow an attacker to be sent a password reset token for the matched user account. (One mitigation in the new releases is to send password reset tokens only to the registered user email address.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19844
- https://github.com/django/django/commit/302a4ff1e8b1c798aab97673909c7a3dfda42c26
- https://github.com/django/django/commit/4d334bea06cac63dc1272abcec545b85136cca0e
- https://github.com/django/django/commit/5b1fbcef7a8bec991ebe7b2a18b5d5a95d72cb70
- https://github.com/django/django/commit/f4cff43bf921fcea6a29b726eb66767f67753fa2
- https://www.djangoproject.com/weblog/2019/dec/18/security-releases
- https://www.debian.org/security/2020/dsa-4598
- https://usn.ubuntu.com/4224-1
- https://security.netapp.com/advisory/ntap-20200110-0003
- https://security.gentoo.org/glsa/202004-17
- https://seclists.org/bugtraq/2020/Jan/9
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HCM2DPUI7TOZWN4A6JFQFUVQ2XGE7GUD
- https://groups.google.com/forum/#!topic/django-announce/3oaB2rVH3a0
- https://github.com/pypa/advisory-database/tree/main/vulns/django/PYSEC-2019-16.yaml
- https://github.com/django/django
- https://github.com/advisories/GHSA-vfq6-hq5r-27r6
- https://docs.djangoproject.com/en/dev/releases/security
- http://packetstormsecurity.com/files/155872/Django-Account-Hijack.html
