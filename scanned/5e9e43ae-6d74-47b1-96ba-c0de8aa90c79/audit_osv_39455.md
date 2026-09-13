# [H] ikev2: unbounded client transform storage can lead to resource exhaustion

## Summary
Severity: High
Advisory: CVE-2026-45769
Aliases: GHSA-hg2g-r464-5593
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-45769
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to versions 7.0.16 and 8.0.5,IKEv2 parser state could grow without bounds while storing client transforms. Repeated crafted UDP traffic may cause Suricata to consume excessive memory, potentially resulting in denial of service. Versions 7.0.16 and 8.0.5 fix the issue. Some workarounds are available. Disable IKE application-layer parsing if it is not needed. Alternatively, use a rule to bypass ike flows after the first packets like `alert ike any any -> any any (sid: 2; flow.pkts_toserver: > 256; bypass; noalert;)`.

## References
- https://forum.suricata.io/t/suricata-8-0-5-and-7-0-16-released/6315
- https://redmine.openinfosecfoundation.org/issues/8415
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45769.json
- https://github.com/OISF/suricata/security/advisories/GHSA-hg2g-r464-5593
- https://nvd.nist.gov/vuln/detail/CVE-2026-45769
