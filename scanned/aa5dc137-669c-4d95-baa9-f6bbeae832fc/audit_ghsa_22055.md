# [C] django-anymail Includes Sensitive Information in Log Files

## Summary
Severity: Critical
Advisory: GHSA-qh9x-mc42-vg4g
CVE: CVE-2018-1000089
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qh9x-mc42-vg4g
Type: github-advisory

## Affected
- PyPI: `django-anymail` — affected >=0.2 <1.4

## Details
Anymail django-anymail version version 0.2 through 1.3 contains a CWE-532, CWE-209 vulnerability in WEBHOOK_AUTHORIZATION setting value that can result in An attacker with access to error logs could fabricate email tracking events. This attack appear to be exploitable via If you have exposed your Django error reports, an attacker could discover your ANYMAIL_WEBHOOK setting and use this to post fabricated or malicious Anymail tracking/inbound events to your app. This vulnerability appears to have been fixed in v1.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000089
- https://github.com/anymail/django-anymail/commit/1a6086f2b58478d71f89bf27eb034ed81aefe5ef
- https://github.com/advisories/GHSA-qh9x-mc42-vg4g
- https://github.com/anymail/django-anymail
- https://github.com/anymail/django-anymail/releases/tag/v1.4
- https://github.com/pypa/advisory-database/tree/main/vulns/django-anymail/PYSEC-2018-46.yaml
