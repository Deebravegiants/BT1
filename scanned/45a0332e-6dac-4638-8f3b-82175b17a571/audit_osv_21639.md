# [H] CVE-2021-44683

## Summary
Severity: High
Advisory: CVE-2021-44683
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-44683
Type: osv

## Details
The DuckDuckGo browser 7.64.4 on iOS allows Address Bar Spoofing due to mishandling of the JavaScript window.open function (used to open a secondary browser window). This could be exploited by tricking users into supplying sensitive information such as credentials, because the address bar would display a legitimate URL, but content would be hosted on the attacker's web site.

## References
- https://www.cybercitadel.com/remote-address-bar-spoofing-and-html-injection-disclosures/
