# [M] Ansible discloses credential information

## Summary
Severity: Medium
Advisory: GHSA-5xm4-jmpw-p6j3
CVE: CVE-2014-4660
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5xm4-jmpw-p6j3
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=0 <1.5.5

## Details
Ansible before 1.5.5 constructs filenames containing user and password fields on the basis of deb lines in `sources.list`, which might allow local users to obtain sensitive credential information in opportunistic circumstances by leveraging existence of a file that uses the `deb http://user:pass@server:port/` format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-4660
- https://github.com/ansible/ansible/commit/c4b5e46054c74176b2446c82d4df1a2610eddc08
- https://github.com/ansible/ansible/blob/release1.5.5/CHANGELOG.md
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2020-202.yaml
- https://security-tracker.debian.org/tracker/CVE-2014-4660
- https://web.archive.org/web/20200229060002/https://www.securityfocus.com/bid/68231
- https://www.openwall.com/lists/oss-security/2014/06/26/19
