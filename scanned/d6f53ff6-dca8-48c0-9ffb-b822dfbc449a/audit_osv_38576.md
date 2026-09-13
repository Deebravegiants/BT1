# [M] ClearanceKit: opfilter system extension can be suspended or signalled by a root process, disabling file-access policy enforcement

## Summary
Severity: Medium
Advisory: CVE-2026-40604
Aliases: GHSA-5r9w-9fg6-266q
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:H/SI:H/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40604
Type: osv

## Details
ClearanceKit intercepts file-system access events on macOS and enforces per-process access policies. Prior to 5.0.6, the opfilter Endpoint Security system extension (bundle ID uk.craigbass.clearancekit.opfilter) can be suspended with SIGSTOP or kill -STOP, or killed with SIGKILL/SIGTERM, by any process running as root. While the extension is suspended, all AUTH Endpoint Security events time out and default to allow, silently disabling ClearanceKit's file-access policy enforcement for the duration of the suspension. This vulnerability is fixed in 5.0.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40604.json
- https://github.com/craigjbass/clearancekit/security/advisories/GHSA-5r9w-9fg6-266q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40604
