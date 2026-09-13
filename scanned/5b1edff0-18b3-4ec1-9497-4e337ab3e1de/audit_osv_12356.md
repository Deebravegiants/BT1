# [H] CVE-2018-11474

## Summary
Severity: High
Advisory: CVE-2018-11474
CVSS: 8.0 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-05-25
Source: https://osv.dev/vulnerability/CVE-2018-11474
Type: osv

## Details
Monstra CMS 3.0.4 has a Session Management Issue in the Administrations Tab. A password change at admin/index.php?id=users&action=edit&user_id=1 does not invalidate a session that is open in a different browser.

## References
- https://github.com/monstra-cms/monstra/issues/444
