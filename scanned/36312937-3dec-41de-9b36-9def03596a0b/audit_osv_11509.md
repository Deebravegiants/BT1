# [H] CVE-2017-8288

## Summary
Severity: High
Advisory: CVE-2017-8288
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-27
Source: https://osv.dev/vulnerability/CVE-2017-8288
Type: osv

## Details
gnome-shell 3.22 through 3.24.1 mishandles extensions that fail to reload, which can lead to leaving extensions enabled in the lock screen. With these extensions, a bystander could launch applications (but not interact with them), see information from the extensions (e.g., what applications you have opened or what music you were playing), or even execute arbitrary commands. It all depends on what extensions a user has enabled. The problem is caused by lack of exception handling in js/ui/extensionSystem.js.

## References
- http://www.securityfocus.com/bid/98070
- https://github.com/EasyScreenCast/EasyScreenCast/issues/46
- https://bugs.kali.org/view.php?id=2513
- https://bugzilla.gnome.org/show_bug.cgi?id=781728
- https://github.com/GNOME/gnome-shell/commit/ff425d1db7082e2755d2a405af53861552acf2a1
