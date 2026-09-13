# [H] cups has Authentication bypass with AuthType Negotiate

## Summary
Severity: High
Advisory: CVE-2025-58060
Aliases: GHSA-4c68-qgrh-rmmq
CVSS: 8.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-58060
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.12 and earlier, when the `AuthType` is set to anything but `Basic`, if the request contains an `Authorization: Basic ...` header, the password is not checked. This results in authentication bypass. Any configuration that allows an `AuthType` that is not `Basic` is affected. Version 2.4.13 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2025/09/11/1
- https://lists.debian.org/debian-lts-announce/2025/09/msg00013.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58060.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-4c68-qgrh-rmmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-58060
- https://github.com/OpenPrinting/cups/commit/595d691075b1d396d2edfaa0a8fd0873a0a1f221
