# [H] CVE-2026-37226

## Summary
Severity: High
Advisory: CVE-2026-37226
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37226
Type: osv

## Details
FlexRIC v2.0.0 crashes when the iApp receives an E42_RIC_SUBSCRIPTION_REQUEST referencing a non-existent E2 Node. The lookup function returns NULL, which is enforced by assert() in Debug builds (SIGABRT) and dereferenced in Release builds (SIGSEGV). A remote unauthenticated attacker can crash the iApp process (port 36422) by sending a subscription request with an arbitrary global_e2_node_id.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37226.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37226.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37226
- https://gitlab.eurecom.fr/mosaic5g/flexric
