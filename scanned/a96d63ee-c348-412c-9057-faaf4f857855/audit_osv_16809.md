# [H] CVE-2019-9847

## Summary
Severity: High
Advisory: CVE-2019-9847
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-05-09
Source: https://osv.dev/vulnerability/CVE-2019-9847
Type: osv

## Details
A vulnerability in LibreOffice hyperlink processing allows an attacker to construct documents containing hyperlinks pointing to the location of an executable on the target users file system. If the hyperlink is activated by the victim the executable target is unconditionally launched. Under Windows and macOS when processing a hyperlink target explicitly activated by the user there was no judgment made on whether the target was an executable file, so such executable targets were launched unconditionally. This issue affects: All LibreOffice Windows and macOS versions prior to 6.1.6; LibreOffice Windows and macOS versions in the 6.2 series prior to 6.2.3.

## References
- https://www.libreoffice.org/about-us/security/advisories/cve-2019-9847/
