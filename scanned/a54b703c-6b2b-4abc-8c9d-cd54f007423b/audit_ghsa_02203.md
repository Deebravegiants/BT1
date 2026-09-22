# [H] Permissions bypass in pleaser

## Summary
Severity: High
Advisory: GHSA-pp74-39w2-v4w9
CVE: CVE-2021-31154
CWE: CWE-340, CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-pp74-39w2-v4w9
Type: github-advisory

## Affected
- crates.io: `pleaser` — affected >=0 <0.4.0

## Details
pleaseedit in pleaser before 0.4.0 uses predictable temporary filenames in /tmp and the target directory. This allows a local attacker to gain full root privileges by staging a symlink attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31154
- https://crates.io/crates/pleaser
- https://gitlab.com/edneville/please
- https://gitlab.com/edneville/please/-/tree/master/src/bin
- https://rustsec.org/advisories/RUSTSEC-2021-0102.html
- https://www.openwall.com/lists/oss-security/2021/05/18/1
