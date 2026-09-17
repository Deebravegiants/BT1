# [M] CVE-2021-35208

## Summary
Severity: Medium
Advisory: CVE-2021-35208
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-07-02
Source: https://osv.dev/vulnerability/CVE-2021-35208
Type: osv

## Details
An issue was discovered in ZmMailMsgView.js in the Calendar Invite component in Zimbra Collaboration Suite 8.8.x before 8.8.15 Patch 23. An attacker could place HTML containing executable JavaScript inside element attributes. This markup becomes unescaped, causing arbitrary markup to be injected into the document.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/8.8.15/P23
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P16
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://blog.sonarsource.com/zimbra-webmail-compromise-via-email
