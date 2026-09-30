# [H] CVE-2024-55553

## Summary
Severity: High
Advisory: CVE-2024-55553
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-06
Source: https://osv.dev/vulnerability/CVE-2024-55553
Type: osv

## Details
In FRRouting (FRR) before 10.3 from 6.0 onward, all routes are re-validated if the total size of an update received via RTR exceeds the internal socket's buffer size, default 4K on most OSes. An attacker can use this to trigger re-parsing of the RIB for FRR routers using RTR by causing more than this number of updates during an update interval (usually 30 minutes). Additionally, this effect regularly occurs organically. Furthermore, an attacker can use this to trigger route validation continuously. Given that routers with large full tables may need more than 30 minutes to fully re-validate the table, continuous issuance/withdrawal of large numbers of ROA may be used to impact the route handling performance of all FRR instances using RPKI globally. Additionally, the re-validation will cause heightened BMP traffic to ingestors. Fixed Versions: 10.0.3, 10.1.2, 10.2.1, >= 10.3.

## References
- https://frrouting.org/security/cve-2024-55553/
- https://github.com/FRRouting/frr/pull/17586/commits/b0800bfdf04b4fcf48504737ebfe4ba7f05268d3
- https://lists.debian.org/debian-lts-announce/2025/01/msg00023.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55553.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55553
