# [M] Ansible Sensitive Files Are Locally Readable

## Summary
Severity: Medium
Advisory: GHSA-5g4v-2pc6-4hh4
CVE: CVE-2014-4658
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5g4v-2pc6-4hh4
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.5.5

## Details
The vault subsystem in Ansible before 1.5.5 does not set the umask before creation or modification of a vault file, which allows local users to obtain sensitive key information by reading a file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4658
- https://github.com/ansible/ansible/commit/a0e027fe362fbc209dbeff2f72d6e95f39885c69
- https://github.com/ansible/ansible
- https://github.com/ansible/ansible/blob/release1.5.5/CHANGELOG.md
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-200.yaml
- https://web.archive.org/web/20210120133853/https://www.securityfocus.com/bid/68233
