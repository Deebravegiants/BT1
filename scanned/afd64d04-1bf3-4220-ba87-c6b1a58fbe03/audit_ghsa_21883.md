# [M] EC-CUBE improperly handles HTTP Host header values

## Summary
Severity: Medium
Advisory: GHSA-pw97-6v74-9w3p
CVE: CVE-2022-25355
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-02-25
Source: https://github.com/advisories/GHSA-pw97-6v74-9w3p
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=3.0.0
- Packagist: `ec-cube/ec-cube` — affected >=4.0.0 <4.1.2

## Details
EC-CUBE 3.0.0 to 3.0.18-p3 and EC-CUBE 4.0.0 to 4.1.1 improperly handle HTTP Host header values, which may lead a remote unauthenticated attacker to direct the vulnerable version of EC-CUBE to send an Email with some forged reissue-password URL to EC-CUBE users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25355
- https://github.com/EC-CUBE/ec-cube
- https://jvn.jp/en/jp/JVN53871926/index.html
- https://www.ec-cube.net/info/weakness/20220221
