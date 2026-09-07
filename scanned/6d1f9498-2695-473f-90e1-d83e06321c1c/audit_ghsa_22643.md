# [H] jQuery File Upload Plugin Unrestricted file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-wxg6-f773-g2f7
CVE: CVE-2014-8739
CWE: CWE-434
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-wxg6-f773-g2f7
Type: github-advisory

## Affected
- Packagist: `blueimp/jquery-file-upload` — affected 6.4.4

## Details
Unrestricted file upload vulnerability in `server/php/UploadHandler.php` in the jQuery File Upload Plugin 6.4.4 for jQuery, as used in the Creative Solutions Creative Contact Form (formerly Sexy Contact Form) before 1.0.0 for WordPress and before 2.0.1 for Joomla!, allows remote attackers to execute arbitrary code by uploading a PHP file with an PHP extension, then accessing it via a direct request to the file in `files/`, as exploited in the wild in October 2014.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8739
- https://wordpress.org/plugins/sexy-contact-form/changelog
- https://www.exploit-db.com/exploits/35057
- https://www.exploit-db.com/exploits/36811
- http://osvdb.org/show/osvdb/113669
- http://osvdb.org/show/osvdb/113673
- http://www.openwall.com/lists/oss-security/2014/11/11/4
- http://www.openwall.com/lists/oss-security/2014/11/11/5
- http://www.openwall.com/lists/oss-security/2014/11/13/3
