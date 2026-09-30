# [H] CVE-2022-0114

## Summary
Severity: High
Advisory: CVE-2022-0114
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-02-12
Source: https://osv.dev/vulnerability/CVE-2022-0114
Type: osv

## Details
Out of bounds memory access in Blink Serial API in Google Chrome prior to 97.0.4692.71 allowed a remote attacker to perform an out of bounds memory read via a crafted HTML page and virtual serial port driver.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5PAGL5M2KGYPN3VEQCRJJE6NA7D5YG5X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQJB6ZPRLKV6WCMX2PRRRQBFAOXFBK6B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRWRAXAFR3JR7XCFWTHC2KALSZKWACCE/
- https://chromereleases.googleblog.com/2022/01/stable-channel-update-for-desktop.html
- https://crbug.com/1267627
