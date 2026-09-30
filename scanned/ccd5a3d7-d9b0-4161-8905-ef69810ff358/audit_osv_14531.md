# [H] CVE-2019-1010123

## Summary
Severity: High
Advisory: CVE-2019-1010123
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-1010123
Type: osv

## Details
MODX Revolution Gallery 1.7.0 is affected by: CWE-434: Unrestricted Upload of File with Dangerous Type. The impact is: Creating file with custom a filename and content. The component is: Filtering user parameters before passing them into phpthumb class. The attack vector is: web request via /assets/components/gallery/connector.php.

## References
- https://modx.today/posts/2018/07/critical-security-vulnerability-in-gallery-1.7.1
- https://modx.pro/security/15912#comment-99640
