# [M] Froxlor Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-j9wr-mj69-cqmv
CVE: CVE-2020-10237
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j9wr-mj69-cqmv
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0

## Details
An issue was discovered in Froxlor through 0.10.15. The installer wrote configuration parameters including passwords into files in /tmp, setting proper permissions only after writing the sensitive data. A local attacker could have disclosed the information if he read the file at the right time, because of _createUserdataConf in install/lib/class.FroxlorInstall.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10237
- https://bugzilla.suse.com/show_bug.cgi?id=1165719
- https://github.com/Froxlor/Froxlor
