# [M] Reflected cross-site scripting in francoisjacquet/rosariosis

## Summary
Severity: Medium
Advisory: GHSA-4cx9-7xqc-2jxm
CVE: CVE-2020-13278
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-4cx9-7xqc-2jxm
Type: github-advisory

## Affected
- Packagist: `francoisjacquet/rosariosis` — affected >=0 <6.5.1

## Details
Reflected Cross-Site Scripting vulnerability in Modules.php in RosarioSIS Student Information System < 6.5.1 allows remote attackers to execute arbitrary web script via embedding javascript or HTML tags in a GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13278
- https://gitlab.com/francoisjacquet/rosariosis/-/commit/9cb4fec5fe177f1d3716708b46d1958eac477ebe
- https://gitlab.com/francoisjacquet/rosariosis/-/issues/282
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13278.json
