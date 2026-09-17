# [M] Suricata segfault on StreamingBufferSlideToOffsetWithRegions

## Summary
Severity: Medium
Advisory: CVE-2024-55627
Aliases: GHSA-h2mv-7gg8-8x7v
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-55627
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. Prior to 7.0.8, a specially crafted TCP stream can lead to a very large buffer overflow while being zero-filled during initialization with memset due to an unsigned integer underflow. The issue has been addressed in Suricata 7.0.8.

## References
- https://redmine.openinfosecfoundation.org/issues/7393
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55627.json
- https://github.com/OISF/suricata/security/advisories/GHSA-h2mv-7gg8-8x7v
- https://nvd.nist.gov/vuln/detail/CVE-2024-55627
- https://github.com/OISF/suricata/commit/282509f70c4ce805098e59535af445362e3e9ebd
- https://github.com/OISF/suricata/commit/8900041405dbb5f9584edae994af2100733fb4be
- https://github.com/OISF/suricata/commit/9a53ec43b13f0039a083950511a18bf6f408e432
