# [M] EVerest has RemoteStop Bypass via BCB Toggle Session Restart

## Summary
Severity: Medium
Advisory: CVE-2026-33015
Aliases: GHSA-pw9q-2287-cchc
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33015
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, even immediately after CSMS performs a RemoteStop (StopTransaction), the EVSE can return to `PrepareCharging` via the EV's BCB toggle, allowing session restart. This breaks the irreversibility of remote stop and can bypass operational/billing/safety controls. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33015.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-pw9q-2287-cchc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33015
