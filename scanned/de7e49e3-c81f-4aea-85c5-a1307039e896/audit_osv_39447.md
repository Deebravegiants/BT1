# [H] Suricata http1: quadratic Content-Disposition processing can lead to denial of service

## Summary
Severity: High
Advisory: CVE-2026-45759
Aliases: GHSA-cfq5-g2v5-6652
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45759
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5, Suricata could repeatedly perform expensive parsing of large HTTP `Content-Disposition` headers during HTTP response body processing. Crafted HTTP traffic could cause excessive CPU usage and denial of service. Versions 7.0.16 and 8.0.5 contain a fix. As a workaround, use a rule like `alert http1 any any -> any any (sid: 1; http.request_header; content: "Content-Disposition:"; startswith; bsize: > 8192; bypass;)`.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8529
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45759.json
- https://github.com/OISF/suricata/security/advisories/GHSA-cfq5-g2v5-6652
- https://nvd.nist.gov/vuln/detail/CVE-2026-45759
