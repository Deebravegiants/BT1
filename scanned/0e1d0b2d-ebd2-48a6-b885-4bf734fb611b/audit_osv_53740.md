# [M] CVE-2023-22332

## Summary
Severity: Medium
Advisory: CVE-2023-22332
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-30
Source: https://osv.dev/vulnerability/CVE-2023-22332
Type: osv

## Details
Information disclosure vulnerability exists in Pgpool-II 4.4.0 to 4.4.1 (4.4 series), 4.3.0 to 4.3.4 (4.3 series), 4.2.0 to 4.2.11 (4.2 series), 4.1.0 to 4.1.14 (4.1 series), 4.0.0 to 4.0.21 (4.0 series), All versions of 3.7 series, All versions of 3.6 series, All versions of 3.5 series, All versions of 3.4 series, and All versions of 3.3 series. A specific database user's authentication information may be obtained by another database user. As a result, the information stored in the database may be altered and/or database may be suspended by a remote attacker who successfully logged in the product with the obtained credentials.

## References
- https://lists.debian.org/debian-lts-announce/2024/12/msg00015.html
- https://jvn.jp/en/jp/JVN72418815/
- https://www.pgpool.net/mediawiki/index.php/Main_Page#News
