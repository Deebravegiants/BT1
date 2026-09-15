# [M] Suricata defrag: IP ID reuse can lead to policy bypass

## Summary
Severity: Medium
Advisory: CVE-2024-37151
Aliases: GHSA-qrp7-g66m-px24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-37151
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. 
Mishandling of multiple fragmented packets using the same IP ID value can lead to packet reassembly failure, which can lead to policy bypass. Upgrade to 7.0.6 or 6.0.20. When using af-packet, enable `defrag` to reduce the scope of the problem.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00029.html
- https://redmine.openinfosecfoundation.org/issues/7041
- https://redmine.openinfosecfoundation.org/issues/7042
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37151.json
- https://github.com/OISF/suricata/security/advisories/GHSA-qrp7-g66m-px24
- https://nvd.nist.gov/vuln/detail/CVE-2024-37151
- https://github.com/OISF/suricata/commit/9d5c4273cb7e5ca65f195f7361f0d848c85180e0
- https://github.com/OISF/suricata/commit/aab7f35c76721df19403a7c0c0025feae12f3b6b
