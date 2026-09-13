# [H] Directory Traversal in Archive_Tar

## Summary
Severity: High
Advisory: GHSA-p8q8-jfcv-g2h2
CVE: CVE-2021-32610
CWE: CWE-59
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-p8q8-jfcv-g2h2
Type: github-advisory

## Affected
- Packagist: `pear/archive_tar` — affected >=0 <1.4.14

## Details
In Archive_Tar before 1.4.14, symlinks can refer to targets outside of the extracted archive, a different vulnerability than CVE-2020-36193.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-32610
- https://github.com/pear/Archive_Tar/commit/7789ebb2f34f9e4adb3a4152ad0d1548930a9755
- https://github.com/pear/Archive_Tar/commit/b5832439b1f37331fb4f87e67fe4f
- https://github.com/pear/Archive_Tar
- https://github.com/pear/Archive_Tar/releases/tag/1.4.14
- https://lists.debian.org/debian-lts-announce/2021/07/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/42GPGVVFTLJYAKRI75IVB5R45NYQGEUR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CAODVMHGL5MHQWQAQTXQ7G7OE3VQZ7LS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/G5LTY6COQYNMMHQJ3QIOJHEWCKD4XDFH
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VJQQYDAOWHD6RDITDRPHFW7WY6BS3V5N
- https://www.drupal.org/sa-core-2021-004
