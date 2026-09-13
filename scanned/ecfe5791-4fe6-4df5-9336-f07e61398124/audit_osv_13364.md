# [C] CVE-2018-19531

## Summary
Severity: Critical
Advisory: CVE-2018-19531
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-19531
Type: osv

## Details
HTTL (aka Hyper-Text Template Language) through 1.0.11 allows remote command execution because the decodeXml function uses java.beans.XMLEncoder unsafely when configured without an xml.codec= setting.

## References
- https://github.com/httl/httl/issues/224
