# [M] Virtualenv Allows Symlink Attack on /tmp/

## Summary
Severity: Medium
Advisory: GHSA-3jhc-wjqf-5f2c
CVE: CVE-2011-4617
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3jhc-wjqf-5f2c
Type: github-advisory

## Affected
- PyPI: `virtualenv` — affected >=0 <1.5

## Details
virtualenv.py in virtualenv before 1.5 allows local users to overwrite arbitrary files via a symlink attack on a certain file in /tmp/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-4617
- https://github.com/pypa/virtualenv/commit/68075ad9ededf7df2c46d385f836c13b729de2ca
- https://bitbucket.org/ianb/virtualenv/changeset/8be37c509fe5
- https://github.com/pypa/advisory-database/tree/main/vulns/virtualenv/PYSEC-2011-23.yaml
- https://github.com/pypa/virtualenv
- https://web.archive.org/web/20200228151935/https://bitbucket.org/ianb/virtualenv/commits/8be37c509fe5
- http://lists.fedoraproject.org/pipermail/package-announce/2012-January/071638.html
- http://lists.fedoraproject.org/pipermail/package-announce/2012-January/071643.html
- http://openwall.com/lists/oss-security/2011/12/19/2
- http://openwall.com/lists/oss-security/2011/12/19/4
- http://openwall.com/lists/oss-security/2011/12/19/5
