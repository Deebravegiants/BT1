# [H] CVE-2026-37234

## Summary
Severity: High
Advisory: CVE-2026-37234
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37234
Type: osv

## Details
FlexRIC v2.0.0 allows a single SCTP connection to bind multiple xapp_ids by sending multiple E42_SETUP_REQUESTs. On disconnect, only the first registered xapp_id's resources are cleaned up; subsequent xapp_ids and their subscriptions remain as stale entries. A remote attacker can exploit this to leak subscription state in the iApp, potentially causing resource exhaustion or state corruption over time.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37234.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37234.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37234
- https://gitlab.eurecom.fr/mosaic5g/flexric
