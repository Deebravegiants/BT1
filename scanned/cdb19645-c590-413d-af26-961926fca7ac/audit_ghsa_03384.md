# [H] Deserialization of Untrusted Data in Archive_Tar

## Summary
Severity: High
Advisory: GHSA-jh5x-hfhg-78jq
CVE: CVE-2020-28948
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-jh5x-hfhg-78jq
Type: github-advisory

## Affected
- Packagist: `pear/archive_tar` — affected >=0 <1.4.11

## Details
Archive_Tar through 1.4.10 allows an unserialization attack because `phar:` is blocked but `PHAR:` is not blocked. See: https://github.com/pear/Archive_Tar/issues/33

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28948
- https://github.com/pear/Archive_Tar/issues/33
- https://github.com/pear/Archive_Tar/commit/0670a05fdab997036a3fc3ef113b8f5922e574da
- https://github.com/pear/Archive_Tar
- https://lists.debian.org/debian-lts-announce/2020/11/msg00045.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/42GPGVVFTLJYAKRI75IVB5R45NYQGEUR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4V35LBRM6HBCXBVCITKQ4UEBTXO2EG7B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5KSFM672XW3X6BR7TVKRD63SLZGKK437
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KWM4CTMEGAC4I2CHYNJVSROY4CVXVEUT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NBYZSHYTIOBK6V7C4N7TP6KIKCRKLVWP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VJQQYDAOWHD6RDITDRPHFW7WY6BS3V5N
- https://security.gentoo.org/glsa/202101-23
- https://www.debian.org/security/2020/dsa-4817
- https://www.drupal.org/sa-core-2020-013
