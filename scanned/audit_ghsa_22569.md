# [M] Froxlor Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-hvgf-2rf7-wrx9
CVE: CVE-2020-10236
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hvgf-2rf7-wrx9
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <0.10.14

## Details
An issue was discovered in Froxlor before 0.10.14. It created files with static names in /tmp during installation if the installation directory was not writable. This allowed local attackers to cause DoS or disclose information out of the config files, because of _createUserdataConf in install/lib/class.FroxlorInstall.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10236
- https://github.com/Froxlor/Froxlor/commit/6b09720ef8a1cc008751dd0ca0140a0597fedce5
- https://bugzilla.suse.com/show_bug.cgi?id=1165718
- https://github.com/Froxlor/Froxlor
- https://github.com/Froxlor/Froxlor/compare/0.10.13...0.10.14
