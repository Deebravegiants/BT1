# [C] CVE-2018-19530

## Summary
Severity: Critical
Advisory: CVE-2018-19530
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-26
Source: https://osv.dev/vulnerability/CVE-2018-19530
Type: osv

## Details
HTTL (aka Hyper-Text Template Language) through 1.0.11 allows remote command execution because the decodeXml function uses XStream unsafely when configured with an xml.codec=httl.spi.codecs.XstreamCodec setting.

## References
- https://github.com/httl/httl/issues/225
