# [H] CVE-2020-15258

## Summary
Severity: High
Advisory: CVE-2020-15258
Aliases: GHSA-5gpx-9976-ggpm
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-10-16
Source: https://osv.dev/vulnerability/CVE-2020-15258
Type: osv

## Details
In Wire before 3.20.x, `shell.openExternal` was used without checking the URL. This vulnerability allows an attacker to execute code on the victims machine by sending messages containing links with arbitrary protocols. The victim has to interact with the link and sees the URL that is opened. The issue was patched by implementing a helper function which checks if the URL's protocol is common. If it is common, the URL will be opened externally. If not, the URL will not be opened and a warning appears for the user informing them that a probably insecure URL was blocked from being executed. The issue is patched in Wire 3.20.x. More technical details about exploitation are available in the linked advisory.

## References
- https://github.com/wireapp/wire-desktop/commit/b3705fffa75a03f055530f55a754face5ac0623b
- https://benjamin-altpeter.de/shell-openexternal-dangers/
- https://github.com/wireapp/wire-desktop/security/advisories/GHSA-5gpx-9976-ggpm
