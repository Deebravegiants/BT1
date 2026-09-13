# [M] Potential Observable Timing Discrepancy in Wagtail

## Summary
Severity: Medium
Advisory: GHSA-jjjr-3jcw-f8v6
CVE: CVE-2020-11037
CWE: CWE-208, CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-05-07
Source: https://github.com/advisories/GHSA-jjjr-3jcw-f8v6
Type: github-advisory

## Affected
- PyPI: `wagtail` — affected >=0 <2.7.3
- PyPI: `wagtail` — affected >=2.8rc1 <2.8.2
- PyPI: `wagtail` — affected >=2.9rc1 <2.9

## Details
### Impact
A potential timing attack exists on pages or documents that have been protected with a shared password through Wagtail's "Privacy" controls. This password check is performed through a character-by-character string comparison, and so an attacker who is able to measure the time taken by this check to a high degree of accuracy could potentially use timing differences to gain knowledge of the password. (This is [understood to be feasible on a local network, but not on the public internet](https://groups.google.com/d/msg/django-developers/iAaq0pvHXuA/fpUuwjK3i2wJ).)

Privacy settings that restrict access to pages / documents on a per-user or per-group basis (as opposed to a shared password) are unaffected by this vulnerability.

### Patches
Patched versions have been released as Wagtail 2.7.3 (for the LTS 2.7 branch), Wagtail 2.8.2 and Wagtail 2.9.

### Workarounds
Site owners who are unable to upgrade to the new versions can use [user- or group-based privacy restrictions](https://docs.wagtail.io/en/stable/advanced_topics/privacy.html) to restrict access to sensitive information; these are unaffected by this vulnerability.

## References
- https://github.com/wagtail/wagtail/security/advisories/GHSA-jjjr-3jcw-f8v6
- https://nvd.nist.gov/vuln/detail/CVE-2020-11037
- https://github.com/wagtail/wagtail/commit/3c030490ed575bb9cd01dfb3a890477dcaeb2edf
- https://github.com/wagtail/wagtail/commit/b76ab57ee859732b9cf9287d380493ab24061090
- https://github.com/wagtail/wagtail/commit/ba9d424bd1ca5ce1910d3de74f5cc07214fbfb11
- https://github.com/wagtail/wagtail/commit/bac3cd0a26b023e595cf2959aae7da15bb5e4340
- https://github.com/pypa/advisory-database/tree/main/vulns/wagtail/PYSEC-2020-153.yaml
- https://github.com/wagtail/wagtail
