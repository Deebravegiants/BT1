# [M] Livestatus command injection in RestAPI

## Summary
Severity: Medium
Advisory: CVE-2024-38865
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-10
Source: https://osv.dev/vulnerability/CVE-2024-38865
Type: osv

## Details
Improper neutralization of livestatus command delimiters in a specific endpoint within RestAPI of Checkmk prior to 2.2.0p39, 2.3.0p25, and 2.1.0p51 (EOL) allows arbitrary livestatus command execution. Exploitation requires the attacker to have a contact group assigned to their user account and for an event to originate from a host with the same contact group or from an event generated with an unknown host.

## References
- https://checkmk.com/werk/17028
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38865.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38865
