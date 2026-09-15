# [H] Froxlor arbitrary code execution via the database configuration options

## Summary
Severity: High
Advisory: GHSA-p29c-jpgj-v57r
CVE: CVE-2020-10235
CWE: CWE-20, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p29c-jpgj-v57r
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <0.10.14

## Details
An issue was discovered in Froxlor before 0.10.14. Remote attackers with access to the installation routine could have executed arbitrary code via the database configuration options that were passed unescaped to exec, because of _backupExistingDatabase in install/lib/class.FroxlorInstall.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10235
- https://github.com/Froxlor/Froxlor/commit/62ce21c9ec393f9962515c88f0c489ace42bf656
- https://github.com/Froxlor/Froxlor/commit/7e361274c5bf687b6a42dd1871f6d75506c5d207
- https://bugzilla.suse.com/show_bug.cgi?id=1165721
- https://github.com/Froxlor/Froxlor
- https://github.com/Froxlor/Froxlor/compare/0.10.13...0.10.14
