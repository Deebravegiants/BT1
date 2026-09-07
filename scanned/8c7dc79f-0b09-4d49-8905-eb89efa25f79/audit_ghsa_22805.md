# [M] Mayan EDMS multiple cross-site scripting (XSS) vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-wpvx-26f7-65q3
CVE: CVE-2014-3840
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wpvx-26f7-65q3
Type: github-advisory

## Affected
- PyPI: `mayan-edms` — affected >=0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in apps/common/templates/calculate_form_title.html in Mayan EDMS 0.13 allow remote authenticated users to inject arbitrary web script or HTML via a (1) tag or the (2) title of a source in a Staging folder, (3) Name field in a bootstrap setup, or Title field in a (4) smart link or (5) web form.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3840
- https://github.com/mayan-edms/mayan-edms/issues/3
- https://github.com/mayan-edms/mayan-edms/commit/398c480c10416d76e7c1dcb607e726e8fc988e72
- https://github.com/mayan-edms/Mayan-EDMS
- https://github.com/pypa/advisory-database/tree/main/vulns/mayan-edms/PYSEC-2014-110.yaml
- http://research.openflare.org/advisories/OF-2014-09/mayan-edbs-storedxss.txt
- http://research.openflare.org/poc/maya-edms/maya-edms_multiple_xss.avi
- http://seclists.org/oss-sec/2014/q2/349
- http://seclists.org/oss-sec/2014/q2/352
- http://www.exploit-db.com/exploits/33493
