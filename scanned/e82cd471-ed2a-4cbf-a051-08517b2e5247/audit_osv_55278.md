# [C] CVE-2025-24201

## Summary
Severity: Critical
Advisory: CVE-2025-24201
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-03-11
Source: https://osv.dev/vulnerability/CVE-2025-24201
Type: osv

## Details
An out-of-bounds write issue was addressed with improved checks to prevent unauthorized actions. This issue is fixed in visionOS 2.3.2, iOS 18.3.2 and iPadOS 18.3.2, macOS Sequoia 15.3.2, Safari 18.3.1, watchOS 11.4, iPadOS 17.7.6, iOS 16.7.11 and iPadOS 16.7.11, iOS 15.8.4 and iPadOS 15.8.4. Maliciously crafted web content may be able to break out of Web Content sandbox. This is a supplementary fix for an attack that was blocked in iOS 17.2. (Apple is aware of a report that this issue may have been exploited in an extremely sophisticated attack against specific targeted individuals on versions of iOS before iOS 17.2.).

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-24201
- https://support.apple.com/en-us/122284
- https://support.apple.com/en-us/122285
- https://support.apple.com/en-us/122372
- https://support.apple.com/en-us/122376
- http://seclists.org/fulldisclosure/2025/Oct/1
- http://seclists.org/fulldisclosure/2025/Oct/31
- https://github.com/JGoyd/Glass-Cage-iOS18-CVE-2025-24085-CVE-2025-24201
- https://support.apple.com/en-us/122283
- https://support.apple.com/en-us/122346
- http://seclists.org/fulldisclosure/2025/Apr/16
- http://seclists.org/fulldisclosure/2025/Apr/7
- http://seclists.org/fulldisclosure/2025/Mar/4
- https://support.apple.com/en-us/122281
- https://support.apple.com/en-us/122345
- http://seclists.org/fulldisclosure/2025/Jun/19
- http://seclists.org/fulldisclosure/2025/Mar/2
- http://seclists.org/fulldisclosure/2025/Mar/5
- http://seclists.org/fulldisclosure/2025/Mar/3
- https://github.com/cisagov/vulnrichment/issues/194
