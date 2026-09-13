# [H] Multiple vulnerabilities through filename manipulation in Archive_Tar

## Summary
Severity: High
Advisory: GHSA-75c5-f4gw-38r9
CVE: CVE-2020-28949
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-04-22
Source: https://github.com/advisories/GHSA-75c5-f4gw-38r9
Type: github-advisory

## Affected
- Packagist: `pear/archive_tar` — affected >=0 <1.4.11

## Details
Archive_Tar through 1.4.10 has `://` filename sanitization only to address phar attacks, and thus any other stream-wrapper attack (such as `file://` to overwrite files) can still succeed. See: https://github.com/pear/Archive_Tar/issues/33

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28949
- https://github.com/pear/Archive_Tar/issues/33
- https://github.com/pear/Archive_Tar/commit/0670a05fdab997036a3fc3ef113b8f5922e574da
- https://www.drupal.org/sa-core-2020-013
- https://www.debian.org/security/2020/dsa-4817
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-28949
- https://security.gentoo.org/glsa/202101-23
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VJQQYDAOWHD6RDITDRPHFW7WY6BS3V5N
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NBYZSHYTIOBK6V7C4N7TP6KIKCRKLVWP
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KWM4CTMEGAC4I2CHYNJVSROY4CVXVEUT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5KSFM672XW3X6BR7TVKRD63SLZGKK437
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4V35LBRM6HBCXBVCITKQ4UEBTXO2EG7B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/42GPGVVFTLJYAKRI75IVB5R45NYQGEUR
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VJQQYDAOWHD6RDITDRPHFW7WY6BS3V5N
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NBYZSHYTIOBK6V7C4N7TP6KIKCRKLVWP
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KWM4CTMEGAC4I2CHYNJVSROY4CVXVEUT
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5KSFM672XW3X6BR7TVKRD63SLZGKK437
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4V35LBRM6HBCXBVCITKQ4UEBTXO2EG7B
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/42GPGVVFTLJYAKRI75IVB5R45NYQGEUR
- https://lists.debian.org/debian-lts-announce/2020/11/msg00045.html
