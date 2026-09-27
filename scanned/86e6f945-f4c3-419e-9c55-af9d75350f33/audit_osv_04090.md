# [H] Apache HTTP Server: HTTP/2 DoS by memory exhaustion on endless continuation frames

## Summary
Severity: High
Advisory: BIT-apache-2024-27316
Aliases: CVE-2024-27316
Ecosystem: Bitnami
Published: 2024-04-06
Source: https://osv.dev/vulnerability/BIT-apache-2024-27316
Type: osv

## Affected
- Bitnami: `apache` — affected >=2.4.17 <2.4.59

## Details
HTTP/2 incoming headers exceeding the limit are temporarily buffered in nghttp2 in order to generate an informative HTTP 413 response. If a client does not stop sending headers, this leads to memory exhaustion.

## References
- https://httpd.apache.org/security/vulnerabilities_24.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FO73U3SLBYFGIW2YKXOK7RI4D6DJSZ2B/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MIUBKSCJGPJ6M2U63V6BKFDF725ODLG7/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QKKDVFWBKIHCC3WXNH3W75WWY4NW42OB/
- https://security.netapp.com/advisory/ntap-20240415-0013/
- http://www.openwall.com/lists/oss-security/2024/04/03/16
- http://www.openwall.com/lists/oss-security/2024/04/04/4
- https://lists.debian.org/debian-lts-announce/2024/05/msg00013.html
- https://www.openwall.com/lists/oss-security/2024/04/03/16
- https://support.apple.com/kb/HT214119
- http://seclists.org/fulldisclosure/2024/Jul/18
- https://nvd.nist.gov/vuln/detail/CVE-2024-27316
- https://www.kb.cert.org/vuls/id/421644
