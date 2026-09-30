# [M] EVerest has race-condition-induced std::map corruption in OCPP 1.6 evse_soc_map

## Summary
Severity: Medium
Advisory: CVE-2026-26072
Aliases: GHSA-9xwc-49c4-p79v
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26072
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to `std::map<std::optional>` concurrent access (container/optional corruption possible). The trigger is EV SoC update with powermeter periodic update and unplugging/SessionFinished status. Version 2026.02.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26072.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-9xwc-49c4-p79v
- https://nvd.nist.gov/vuln/detail/CVE-2026-26072
