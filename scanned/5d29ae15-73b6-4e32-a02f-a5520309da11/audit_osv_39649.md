# [H] Suricata http2: decompression bomb can cause denial of service in Suricata

## Summary
Severity: High
Advisory: CVE-2026-46387
Aliases: GHSA-45p7-j5wm-8wrx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-46387
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, Suricata's HTTP/2 decompression path could grow the decompressed response-body buffer without an effective upper bound. A crafted HTTP/2 DATA payload using a high compression ratio, such as gzip, deflate, or brotli compressed data, could cause Suricata to allocate excessive memory while decompressing the payload. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, disable HTTP2.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8513
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46387.json
- https://github.com/OISF/suricata/security/advisories/GHSA-45p7-j5wm-8wrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-46387
