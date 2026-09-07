# [H] PHP Code Injection by malicious block or filename in Smarty

## Summary
Severity: High
Advisory: GHSA-634x-pc3q-cf4c
CVE: CVE-2022-29221
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-634x-pc3q-cf4c
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.45
- Packagist: `smarty/smarty` — affected >=4.0.0 <4.1.1

## Details
### Impact
Template authors could inject php code by choosing a malicous {block} name or {include} file name. Sites that cannot fully trust template authors should update asap.

### Patches
Please upgrade to the most recent version of Smarty v3 or v4.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Smarty repo](https://github.com/smarty-php/smarty)

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-634x-pc3q-cf4c
- https://nvd.nist.gov/vuln/detail/CVE-2022-29221
- https://github.com/smarty-php/smarty/commit/64ad6442ca1da31cefdab5c9874262b702cccddd
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2022-29221.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v3.1.45
- https://github.com/smarty-php/smarty/releases/tag/v4.1.1
- https://lists.debian.org/debian-lts-announce/2022/05/msg00044.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BRAJVDRGCIY5UZ2PQHKDTT7RMKG6WJQQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L777JIBIWJV34HS7LXPIDWASG7TT4LNI
- https://security.gentoo.org/glsa/202209-09
- https://www.debian.org/security/2022/dsa-5151
