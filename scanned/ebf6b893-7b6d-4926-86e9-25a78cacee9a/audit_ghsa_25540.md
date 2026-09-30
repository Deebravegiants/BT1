# [H] Files or Directories Accessible to External Parties in Adminer

## Summary
Severity: High
Advisory: GHSA-rxfq-3vpc-vv72
CVE: CVE-2021-43008
CWE: CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-rxfq-3vpc-vv72
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=1.12.0 <4.6.3

## Details
Improper Access Control in Adminer versions 1.12.0 to 4.6.2 (fixed in version 4.6.3) allows an attacker to achieve Arbitrary File Read on the remote server by requesting the Adminer to connect to a remote MySQL database.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43008
- https://github.com/vrana/adminer
- https://github.com/vrana/adminer/releases/tag/v4.6.3
- https://lists.debian.org/debian-lts-announce/2022/05/msg00012.html
- https://podalirius.net/en/cves/2021-43008
- https://sansec.io/research/adminer-4.6.2-file-disclosure-vulnerability
- https://www.adminer.org
