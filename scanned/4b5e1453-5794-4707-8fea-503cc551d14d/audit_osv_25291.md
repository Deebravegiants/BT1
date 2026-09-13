# [M] Incorrect signature verification in django-ses

## Summary
Severity: Medium
Advisory: CVE-2023-33185
Aliases: GHSA-qg36-9jxh-fj25, PYSEC-2023-82
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-33185
Type: osv

## Details
Django-SES is a drop-in mail backend for Django. The django_ses library implements a mail backend for Django using AWS Simple Email Service. The library exports the `SESEventWebhookView class` intended to receive signed requests from AWS to handle email bounces, subscriptions, etc. These requests are signed by AWS and are verified by django_ses, however the verification of this signature was found to be flawed as it allowed users to specify arbitrary public certificates. This issue was patched in version 3.5.0.

## References
- https://github.com/django-ses/django-ses/blob/3d627067935876487f9938310d5e1fbb249a7778/CVE/001-cert-url-signature-verification.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33185.json
- https://github.com/django-ses/django-ses/security/advisories/GHSA-qg36-9jxh-fj25
- https://nvd.nist.gov/vuln/detail/CVE-2023-33185
- https://github.com/django-ses/django-ses/commit/b71b5f413293a13997b6e6314086cb9c22629795
