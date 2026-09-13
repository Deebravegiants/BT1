# [C] CVE-2020-27197

## Summary
Severity: Critical
Advisory: CVE-2020-27197
Aliases: GHSA-836c-xg97-8p4h, PYSEC-2020-59
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-17
Source: https://osv.dev/vulnerability/CVE-2020-27197
Type: osv

## Details
TAXII libtaxii through 1.1.117, as used in EclecticIQ OpenTAXII through 0.2.0 and other products, allows SSRF via an initial http:// substring to the parse method, even when the no_network setting is used for the XML parser. NOTE: the vendor points out that the parse method "wraps the lxml library" and that this may be an issue to "raise ... to the lxml group.

## References
- http://packetstormsecurity.com/files/159662/Libtaxii-1.1.117-OpenTaxi-0.2.0-Server-Side-Request-Forgery.html
- https://github.com/TAXIIProject/libtaxii/issues/246
- https://github.com/eclecticiq/OpenTAXII/issues/176
