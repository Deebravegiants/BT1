# [C] CVE-2018-14939

## Summary
Severity: Critical
Advisory: CVE-2018-14939
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-05
Source: https://osv.dev/vulnerability/CVE-2018-14939
Type: osv

## Details
The get_app_path function in desktop/unx/source/start.c in LibreOffice through 6.0.5 mishandles the realpath function in certain environments such as FreeBSD libc, which might allow attackers to cause a denial of service (buffer overflow and application crash) or possibly have unspecified other impact if LibreOffice is automatically launched during web browsing with pathnames controlled by a remote web site.

## References
- http://www.securityfocus.com/bid/105047
- https://bugs.documentfoundation.org/show_bug.cgi?id=118514
