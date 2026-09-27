# [H] CVE-2026-37233

## Summary
Severity: High
Advisory: CVE-2026-37233
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37233
Type: osv

## Details
FlexRIC v2.0.0 contains an authorization bypass in the iApp's xApp isolation mechanism. The equality function eq_xapp_ric_gen_id() in src/ric/iApp/xapp_ric_id.c compares m0->xapp_id against itself (m0->xapp_id) instead of the other argument (m1->xapp_id), effectively ignoring the xApp identity dimension. A malicious xApp connected to the iApp (port 36422) can delete any other xApp's subscriptions by sending an E42_RIC_SUBSCRIPTION_DELETE_REQUEST with a matching ric_gen_id. This breaks multi-tenant isolation in any deployment with multiple xApps sharing the same RIC.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37233.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37233.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37233
- https://gitlab.eurecom.fr/mosaic5g/flexric
