# [C] lwIP snmpv3 USM snmp_msg.c snmp_parse_inbound_frame stack-based overflow

## Summary
Severity: Critical
Advisory: CVE-2026-8836
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-8836
Type: osv

## Details
A vulnerability was found in lwIP up to 2.2.1. Affected is the function snmp_parse_inbound_frame of the file src/apps/snmp/snmp_msg.c of the component snmpv3 USM Handler. Performing a manipulation of the argument msgAuthenticationParameters results in stack-based buffer overflow. The attack may be initiated remotely. The patch is named 0c957ec03054eb6c8205e9c9d1d05d90ada3898c. It is suggested to install a patch to address this issue. Two separate issue reports were submitted to the project. Their processing was merged as a duplicate.

## References
- https://savannah.nongnu.org/bugs/?68055
- https://savannah.nongnu.org/bugs/?68194
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8836.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8836
- https://vuldb.com/cve/CVE-2026-8836
- https://vuldb.com/submit/829798
- https://vuldb.com/vuln/364474
- https://vuldb.com/vuln/364474/cti
- https://cgit.git.savannah.gnu.org/cgit/lwip.git/commit/?id=0c957ec03054eb6c8205e9c9d1d05d90ada3898c
- https://github.com/lwip-tcpip/lwip/commit/0c957ec03054eb6c8205e9c9d1d05d90ada3898c
