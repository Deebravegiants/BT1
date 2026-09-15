# [H] CVE-2024-8383

## Summary
Severity: High
Advisory: CVE-2024-8383
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8383
Type: osv

## Details
Firefox normally asks for confirmation before asking the operating system to find an application to handle a scheme that the browser does not support. It did not ask before doing so for the Usenet-related schemes news: and snews:. Since most operating systems don't have a trusted newsreader installed by default, an unscrupulous program that the user downloaded could register itself as a handler. The website that served the application download could then launch that application at will. This vulnerability affects Firefox < 130, Firefox ESR < 128.2, and Firefox ESR < 115.15.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00025.html
- https://www.mozilla.org/security/advisories/mfsa2024-39/
- https://www.mozilla.org/security/advisories/mfsa2024-40/
- https://www.mozilla.org/security/advisories/mfsa2024-41/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1908496
