# [H] EVerest's use of assert functions can potentially lead to denial of service

## Summary
Severity: High
Advisory: CVE-2025-68134
Aliases: GHSA-cxc5-rrj5-8pf3
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68134
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.10.0, the use of the `assert` function to handle errors frequently causes the module to crash. This is particularly critical because the manager shuts down all other modules and exits when any one of them terminates, leading to a denial of service. In a context where a manager handles multiple EVSE, this would also impact other users. Version 2025.10.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68134.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-cxc5-rrj5-8pf3
- https://nvd.nist.gov/vuln/detail/CVE-2025-68134
