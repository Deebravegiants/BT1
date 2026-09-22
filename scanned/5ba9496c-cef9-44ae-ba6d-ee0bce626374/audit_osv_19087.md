# [H] CVE-2020-7062

## Summary
Severity: High
Advisory: CVE-2020-7062
Aliases: BIT-libphp-2020-7062, BIT-php-2020-7062, BIT-php-min-2020-7062
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-27
Source: https://osv.dev/vulnerability/CVE-2020-7062
Type: osv

## Details
In PHP versions 7.2.x below 7.2.28, 7.3.x below 7.3.15 and 7.4.x below 7.4.3, when using file upload functionality, if upload progress tracking is enabled, but session.upload_progress.cleanup is set to 0 (disabled), and the file upload fails, the upload procedure would try to clean up data that does not exist and encounter null pointer dereference, which would likely lead to a crash.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00023.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00034.html
- https://security.gentoo.org/glsa/202003-57
- https://usn.ubuntu.com/4330-1/
- https://www.debian.org/security/2020/dsa-4717
- https://www.debian.org/security/2020/dsa-4719
- https://www.tenable.com/security/tns-2021-14
- https://bugs.php.net/bug.php?id=79221
