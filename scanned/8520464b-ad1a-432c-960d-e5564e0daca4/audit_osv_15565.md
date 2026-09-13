# [H] CVE-2019-17358

## Summary
Severity: High
Advisory: CVE-2019-17358
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-17358
Type: osv

## Details
Cacti through 1.2.7 is affected by multiple instances of lib/functions.php unsafe deserialization of user-controlled data to populate arrays. An authenticated attacker could use this to influence object data values and control actions taken by Cacti or potentially cause memory corruption in the PHP module.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00048.html
- https://seclists.org/bugtraq/2020/Jan/25
- https://www.darkmatter.ae/xen1thlabs/
- https://lists.debian.org/debian-lts-announce/2019/12/msg00014.html
- https://people.canonical.com/~ubuntu-security/cve/2019/CVE-2019-17358.html
- https://security.gentoo.org/glsa/202003-40
- https://www.debian.org/security/2020/dsa-4604
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2019-17358
- https://github.com/Cacti/cacti/issues/3026
- https://github.com/Cacti/cacti/commit/adf221344359f5b02b8aed43dfb6b33ae5d708c8
- https://github.com/Cacti/cacti/blob/79f29cddb5eb05cbaff486cd634285ef1fed9326/lib/functions.php#L3109
