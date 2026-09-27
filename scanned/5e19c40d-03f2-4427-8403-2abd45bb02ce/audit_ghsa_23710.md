# [H] attic has improper verification of unencrypted backups

## Summary
Severity: High
Advisory: GHSA-5x6q-ffwj-8vcf
CVE: CVE-2015-4082
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5x6q-ffwj-8vcf
Type: github-advisory

## Affected
- PyPI: `attic` — affected >=0 <0.15

## Details
attic before 0.15 does not confirm unencrypted backups with the user, which allows remote attackers with read and write privileges for the encrypted repository to obtain potentially sensitive information by changing the manifest type byte of the repository to "unencrypted / without key file".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-4082
- https://github.com/jborg/attic/issues/271
- https://github.com/jborg/attic/commit/78f9ad1faba7193ca7f0acccbc13b1ff6ebf9072
- https://github.com/jborg/attic
- https://github.com/pypa/advisory-database/tree/main/vulns/attic/PYSEC-2017-6.yaml
- https://web.archive.org/web/20200517225455/http://www.securityfocus.com/bid/74821
- http://www.openwall.com/lists/oss-security/2015/05/31/3
- http://www.securityfocus.com/bid/74821
