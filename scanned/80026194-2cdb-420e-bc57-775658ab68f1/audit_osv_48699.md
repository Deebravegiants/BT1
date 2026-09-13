# [H] CVE-2018-11646

## Summary
Severity: High
Advisory: CVE-2018-11646
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2018-11646
Type: osv

## Details
webkitFaviconDatabaseSetIconForPageURL and webkitFaviconDatabaseSetIconURLForPageURL in UIProcess/API/glib/WebKitFaviconDatabase.cpp in WebKit, as used in WebKitGTK+ through 2.21.3, mishandle an unset pageURL, leading to an application crash.

## References
- https://security.gentoo.org/glsa/201808-04
- https://bugzilla.gnome.org/show_bug.cgi?id=795740
- https://bugs.webkit.org/show_bug.cgi?id=186164
- https://www.exploit-db.com/exploits/44842/
- https://www.exploit-db.com/exploits/44876/
