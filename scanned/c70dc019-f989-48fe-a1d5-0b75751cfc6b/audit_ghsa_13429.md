# [H] Archive_Tar contains Potential RCE if filename starts with phar://

## Summary
Severity: High
Advisory: GHSA-3q76-jq6m-573p
CVE: CVE-2018-1000888
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-07
Source: https://github.com/advisories/GHSA-3q76-jq6m-573p
Type: github-advisory

## Affected
- Packagist: `pear/archive_tar` — affected >=0 <1.4.4

## Details
PEAR Archive_Tar version 1.4.3 and earlier contains a CWE-502, CWE-915 vulnerability in the Archive_Tar class. There are several file operations with `$v_header['filename']` as parameter (such as file_exists, is_file, is_dir, etc). When extract is called without a specific prefix path, we can trigger unserialization by crafting a tar file with `phar://[path_to_malicious_phar_file]` as path. Object injection can be used to trigger destruct in the loaded PHP classes, e.g. the Archive_Tar class itself. With Archive_Tar object injection, arbitrary file deletion can occur because `@unlink($this->_temp_tarname)` is called. If another class with useful gadget is loaded, it may possible to cause remote code execution that can result in files being deleted or possibly modified. This vulnerability appears to have been fixed in 1.4.4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000888
- https://github.com/pear/Archive_Tar/commit/59ace120ac5ceb5f0d36e40e48e1884de1badf76
- https://github.com/FriendsOfPHP/security-advisories/blob/master/pear/archive_tar/CVE-2018-1000888.yaml
- https://github.com/pear/Archive_Tar
- https://lists.debian.org/debian-lts-announce/2019/02/msg00020.html
- https://pear.php.net/bugs/bug.php?id=23782
- https://security.gentoo.org/glsa/202006-14
- https://usn.ubuntu.com/3857-1
- https://web.archive.org/web/20210328115328/https://cdn2.hubspot.net/hubfs/3853213/us-18-Thomas-It's-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-....pdf
- https://web.archive.org/web/20220524160841/https://blog.sonarsource.com/new-php-exploitation-technique?redirect=rips
- https://www.debian.org/security/2019/dsa-4378
- https://www.exploit-db.com/exploits/46108
