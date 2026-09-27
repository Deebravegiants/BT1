# [H] Composer's missing argument delimiter can lead to code execution via VCS repository URLs or source download URLs on systems with Mercurial

## Summary
Severity: High
Advisory: GHSA-h5h8-pc6h-jvvx
CVE: CVE-2021-29472
CWE: CWE-88, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-29
Source: https://github.com/advisories/GHSA-h5h8-pc6h-jvvx
Type: github-advisory

## Affected
- Packagist: `composer/composer` — affected >=0 <1.10.22
- Packagist: `composer/composer` — affected >=2.0.0-alpha1 <2.0.13

## Details
URLs for Mercurial repositories in the root composer.json and package source download URLs are not sanitized correctly. Specifically crafted URL values allow commands to be executed in the HgDriver if hg/Mercurial is installed on the system.

### Impact
- The impact to Composer users directly is limited as the composer.json file is typically under their own control and source download URLs can only be supplied by third party Composer repositories they explicitly trust to download and execute source code from, e.g. Composer plugins.
- The main impact is to services passing user input to Composer, including Packagist.org and Private Packagist. This allowed users to trigger remote command injection. The vulnerability has been patched on Packagist.org and Private Packagist within 12h of receiving the initial vulnerability report and based on a review of logs, to the best of our knowledge, was not abused by anyone.
- Other services/tools using VcsRepository/VcsDriver or derivatives may also be vulnerable and should upgrade their composer/composer dependency immediately

### Patches
1.10.22 and 2.0.13 include patches for this issue.

## References
- https://github.com/composer/composer/security/advisories/GHSA-h5h8-pc6h-jvvx
- https://nvd.nist.gov/vuln/detail/CVE-2021-29472
- https://blog.sonarsource.com/php-supply-chain-attack-on-composer
- https://getcomposer.org
- https://github.com/FriendsOfPHP/security-advisories/blob/master/composer/composer/CVE-2021-29472.yaml
- https://github.com/composer/composer
- https://lists.debian.org/debian-lts-announce/2021/05/msg00009.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FAQUAMGO4Q4BLNZ2OH4CXQD7UK4IO2GE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KN3DMFH42BJW45VT6FYF2RXKC26D6VC2
- https://www.debian.org/security/2021/dsa-4907
