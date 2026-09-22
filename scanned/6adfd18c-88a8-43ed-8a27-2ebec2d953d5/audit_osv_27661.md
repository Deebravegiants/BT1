# [M] Suricata http2: header handling evasion

## Summary
Severity: Medium
Advisory: CVE-2024-24568
Aliases: GHSA-gv29-5hqw-5h8c
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-24568
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine.  Prior to 7.0.3, the rules inspecting HTTP2 headers can get bypassed by crafted traffic. The vulnerability has been patched in 7.0.3.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GOCOBFUTIFHOP2PZOH4ENRFXRBHIRKK4/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZXJIT7R53ZXROO3I256RFUWTIW4ECK6P/
- https://redmine.openinfosecfoundation.org/issues/6717
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24568.json
- https://github.com/OISF/suricata/security/advisories/GHSA-gv29-5hqw-5h8c
- https://nvd.nist.gov/vuln/detail/CVE-2024-24568
- https://github.com/OISF/suricata/commit/478a2a38f54e2ae235f8486bff87d7d66b6307f0
