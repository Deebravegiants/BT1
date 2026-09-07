# [M] Terms and Conditions Module vulnerable to Open Redirect

## Summary
Severity: Medium
Advisory: GHSA-6rmf-cv6p-4h27
CVE: CVE-2022-4589
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-17
Source: https://github.com/advisories/GHSA-6rmf-cv6p-4h27
Type: github-advisory

## Affected
- PyPI: `django-termsandconditions` — affected >=0 <2.0.11

## Details
A vulnerability has been found in cyface Terms and Conditions Module up to 2.0.10 and classified as problematic. Affected by this vulnerability is the function returnTo of the file termsandconditions/views.py. The manipulation leads to open redirect. The attack can be launched remotely. Upgrading to version 2.0.11 can address this issue. The name of the patch is 03396a1c2e0af95e12a45c5faef7e47a4b513e1a. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216175.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4589
- https://github.com/cyface/django-termsandconditions/pull/239
- https://github.com/cyface/django-termsandconditions/commit/03396a1c2e0af95e12a45c5faef7e47a4b513e1a
- https://github.com/cyface/django-termsandconditions
- https://github.com/cyface/django-termsandconditions/releases/tag/v2.0.10
- https://github.com/cyface/django-termsandconditions/releases/tag/v2.0.11
- https://vuldb.com/?id.216175
