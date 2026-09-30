# [M] EVerest: OCPP 2.0.1 EV SoC Update Race Causes Charge Point Crash

## Summary
Severity: Medium
Advisory: CVE-2026-26070
Aliases: GHSA-498x-w527-jp3c
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26070
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to `std::map<std::optional>` concurrent access (container/optional corruption possible). The trigger is an EV SoC update with powermeter periodic update and unplugging/SessionFinished state. Version 2026.2.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26070.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-498x-w527-jp3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-26070
