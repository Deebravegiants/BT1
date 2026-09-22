# [M] CVE-2022-20132

## Summary
Severity: Medium
Advisory: CVE-2022-20132
Aliases: A-188677105, ASB-A-188677105
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-06-15
Source: https://osv.dev/vulnerability/CVE-2022-20132
Type: osv

## Details
In lg_probe and related functions of hid-lg.c and other USB HID files, there is a possible out of bounds read due to improper input validation. This could lead to local information disclosure if a malicious USB HID device were plugged in, with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-188677105References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2022-06-01
