# [H] CVE-2020-10252

## Summary
Severity: High
Advisory: CVE-2020-10252
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2021-02-19
Source: https://osv.dev/vulnerability/CVE-2020-10252
Type: osv

## Details
An issue was discovered in ownCloud before 10.4. Because of an SSRF issue (via the apps/files_sharing/external remote parameter), an authenticated attacker can interact with local services blindly (aka Blind SSRF) or conduct a Denial Of Service attack.

## References
- https://owncloud.com/security-advisories/ssrf-in-add-to-your-owncloud-functionality/
- https://owncloud.org/changelog/server/
- https://blog.hacktivesecurity.com/index.php?controller=post&action=view&id_post=44
