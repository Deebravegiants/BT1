# [M] Ansible sets unsafe permissions for sources.list

## Summary
Severity: Medium
Advisory: GHSA-6667-f46p-pg88
CVE: CVE-2014-4659
CWE: CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6667-f46p-pg88
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.5.5

## Details
Ansible before 1.5.5 sets 0644 permissions for `sources.list`, which might allow local users to obtain sensitive credential information in opportunistic circumstances by reading a file that uses the `&quot;deb http://user:pass@server:port/&quot;` format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4659
- https://github.com/ansible/ansible/commit/a0e027fe362fbc209dbeff2f72d6e95f39885c69
- https://github.com/ansible/ansible/blob/release1.5.5/CHANGELOG.md
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-201.yaml
- https://web.archive.org/web/20200229060001/https://www.securityfocus.com/bid/68234
