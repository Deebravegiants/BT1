# [H] wger Workout Manager Cross-Site Request Forgery vulnerability

## Summary
Severity: High
Advisory: GHSA-wrw3-qmqw-4x9w
CVE: CVE-2023-38759
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-08
Source: https://github.com/advisories/GHSA-wrw3-qmqw-4x9w
Type: github-advisory

## Affected
- PyPI: `wger` — affected >=0

## Details
Cross Site Request Forgery (CSRF) vulnerability in wger Project wger Workout Manager 2.2.0a3 allows a remote attacker to gain privileges via the `user-management` feature in the `gym/views/gym.py`, `templates/gym/reset_user_password.html`, `templates/user/overview.html`, `core/views/user.py`, and `templates/user/preferences.html`, `core/forms.py` components.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-38759
- https://github.com/0x72303074/CVE-Disclosures
- https://github.com/pypa/advisory-database/tree/main/vulns/wger/PYSEC-2023-144.yaml
- https://github.com/wger-project/wger
- https://wger.de
