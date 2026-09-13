# [C] CVE-2020-10282

## Summary
Severity: Critical
Advisory: CVE-2020-10282
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-03
Source: https://osv.dev/vulnerability/CVE-2020-10282
Type: osv

## Details
The Micro Air Vehicle Link (MAVLink) protocol presents no authentication mechanism on its version 1.0 (nor authorization) whichs leads to a variety of attacks including identity spoofing, unauthorized access, PITM attacks and more. According to literature, version 2.0 optionally allows for package signing which mitigates this flaw. Another source mentions that MAVLink 2.0 only provides a simple authentication system based on HMAC. This implies that the flying system overall should add the same symmetric key into all devices of network. If not the case, this may cause a security issue, that if one of the devices and its symmetric key are compromised, the whole authentication system is not reliable.

## References
- https://github.com/rligocki/Diploma_thesis_px4
