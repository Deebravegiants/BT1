# [H] Suricata http: heap use after free with  http.request_header and http.response_header keywords

## Summary
Severity: High
Advisory: CVE-2024-23839
Aliases: GHSA-qxj6-hr2p-mmc7
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-23839
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine.  Prior to 7.0.3, specially crafted traffic can cause a heap use after free if the ruleset uses the http.request_header or http.response_header keyword.  The vulnerability has been patched in 7.0.3.  To work around the vulnerability, avoid the http.request_header and http.response_header keywords.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GOCOBFUTIFHOP2PZOH4ENRFXRBHIRKK4/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZXJIT7R53ZXROO3I256RFUWTIW4ECK6P/
- https://redmine.openinfosecfoundation.org/issues/6657
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23839.json
- https://github.com/OISF/suricata/security/advisories/GHSA-qxj6-hr2p-mmc7
- https://nvd.nist.gov/vuln/detail/CVE-2024-23839
- https://github.com/OISF/suricata/commit/cd731fcaf42e5f7078c9be643bfa0cee2ad53e8f
