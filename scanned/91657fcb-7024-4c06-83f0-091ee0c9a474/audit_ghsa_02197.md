# [H] Permissions bypass in pleaser

## Summary
Severity: High
Advisory: GHSA-vc5p-j8vw-mc6x
CVE: CVE-2021-31155
CWE: CWE-269, CWE-279
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-vc5p-j8vw-mc6x
Type: github-advisory

## Affected
- crates.io: `pleaser` — affected >=0 <0.4.0

## Details
Failure to normalize the umask in pleaser before 0.4.0 allows a local attacker to gain full root privileges if they are allowed to execute at least one command.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31155
- https://crates.io/crates/pleaser
- https://gitlab.com/edneville/please
- https://gitlab.com/edneville/please/-/tree/master/src/bin
- https://rustsec.org/advisories/RUSTSEC-2021-0101.html
- https://www.openwall.com/lists/oss-security/2021/05/18/1
