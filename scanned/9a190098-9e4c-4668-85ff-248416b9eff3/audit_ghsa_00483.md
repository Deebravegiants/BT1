# [H] conference-scheduler-cli Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-cf3c-fffp-34qh
CVE: CVE-2018-14572
CWE: CWE-502, CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-29
Source: https://github.com/advisories/GHSA-cf3c-fffp-34qh
Type: github-advisory

## Affected
- PyPI: `conference-scheduler-cli` — affected >=0

## Details
In conference-scheduler-cli, a pickle.load call on imported data allows remote attackers to execute arbitrary code via a crafted .pickle file, as demonstrated by Python code that contains an os.system call.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14572
- https://github.com/PyconUK/ConferenceScheduler-cli/issues/19
- https://github.com/PyconUK/ConferenceScheduler-cli
- https://github.com/advisories/GHSA-cf3c-fffp-34qh
- https://github.com/pypa/advisory-database/tree/main/vulns/conference-scheduler-cli/PYSEC-2018-64.yaml
- https://joel-malwarebenchmark.github.io/blog/2020/04/25/cve-2018-14572-conference-scheduler-cli
