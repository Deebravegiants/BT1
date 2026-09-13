# [M] Suricata decode_base64: signature can do large memory allocation

## Summary
Severity: Medium
Advisory: CVE-2025-29917
Aliases: GHSA-x8c9-8553-j9px
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2025-29917
Type: osv

## Details
Suricata is a network Intrusion Detection System, Intrusion Prevention System and Network Security Monitoring engine. The bytes setting in the decode_base64 keyword is not properly limited. Due to this, signatures using the keyword and setting can cause large memory allocations of up to 4 GiB per thread. This vulnerability is fixed in 7.0.9.

## References
- https://redmine.openinfosecfoundation.org/issues/7613
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29917.json
- https://github.com/OISF/suricata/security/advisories/GHSA-x8c9-8553-j9px
- https://nvd.nist.gov/vuln/detail/CVE-2025-29917
- https://github.com/OISF/suricata/commit/32d0bd2bbb4d486623dec85a94952fde2515f2f0
