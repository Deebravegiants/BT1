# [M] OpenSIPS has memory leak in cJSON lib

## Summary
Severity: Medium
Advisory: CVE-2023-28096
Aliases: GHSA-2mg2-g46r-j4qr
CVSS: 4.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-28096
Type: osv

## Details
OpenSIPS, a Session Initiation Protocol (SIP) server implementation, has a memory leak starting in the 2.3 branch and priot to versions 3.1.8 and 3.2.5. The memory leak was detected in the function `parse_mi_request` while performing coverage-guided fuzzing. This issue can be reproduced by sending multiple requests of the form `{"jsonrpc": "2.0","method": "log_le`. This malformed message was tested against an instance of OpenSIPS via FIFO transport layer and was found to increase the memory consumption over time.

To abuse this memory leak, attackers need to reach the management interface (MI) which typically should only be exposed on trusted interfaces. In cases where the MI is exposed to the internet without authentication, abuse of this issue will lead to memory exhaustion which may affect the underlying system’s availability. No authentication is typically required to reproduce this issue. On the other hand, memory leaks may occur in other areas of OpenSIPS where the cJSON library is used for parsing JSON objects.

The issue has been fixed in versions 3.1.8 and 3.2.5.

## References
- https://opensips.org/pub/audit-2022/opensips-audit-technical-report-full.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28096.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-2mg2-g46r-j4qr
- https://nvd.nist.gov/vuln/detail/CVE-2023-28096
- https://github.com/OpenSIPS/opensips/commit/417568707520af25ec5c5dd91da18e6db3649dcb
