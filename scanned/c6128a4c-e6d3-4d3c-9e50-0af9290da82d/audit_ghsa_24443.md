# [H] GramAddict bot uses dependency with reverse tcp backdoor

## Summary
Severity: High
Advisory: GHSA-q5h6-49gg-2wfg
CVE: CVE-2020-36245
CWE: CWE-306, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-q5h6-49gg-2wfg
Type: github-advisory

## Affected
- PyPI: `GramAddict` — affected >=0 <1.2.5

## Details
GramAddict before 1.2.5 allows remote attackers to execute arbitrary code because of use of UIAutomator2 and ATX-Agent. The attacker must be able to reach TCP port 7912, e.g., by being on the same Wi-Fi network.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36245
- https://github.com/GramAddict/bot/issues/134
- https://github.com/GramAddict/bot/pull/183
- https://github.com/GramAddict/bot/commit/b9d11691b2fb13749c3cd0f75c70ee31242053ce
- https://github.com/GramAddict/bot
- https://github.com/pypa/advisory-database/tree/main/vulns/gramaddict/PYSEC-2021-65.yaml
