# [M] In EVerest, by default, the EV is responsible for closing the connection if the module encounters an error during request processing

## Summary
Severity: Medium
Advisory: CVE-2025-68139
Aliases: GHSA-wqh4-pj54-6xv9
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68139
Type: osv

## Details
EVerest is an EV charging software stack. In all versions up to and including 2025.12.1, the default value for `terminate_connection_on_failed_response` is `False`, which leaves the responsibility for session and connection termination to the EV. In this configuration, any errors encountered by the module are logged but do not trigger countermeasures such as session and connection reset or termination. This could be abused by a malicious user in order to exploit other weaknesses or vulnerabilities. While the default will stay at the setting that is described as potentially problematic in this reported issue, a mitigation is available by changing the `terminate_connection_on_failed_response`  setting to `true`. However this cannot be set to this value by default since it can trigger errors in vehicle ECUs requiring ECU resets and lengthy unavailability in charging for vehicles. The maintainers judge this to be a much more important workaround then short-term unavailability of an EVSE, therefore this setting will stay at the current value.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68139.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-wqh4-pj54-6xv9
- https://nvd.nist.gov/vuln/detail/CVE-2025-68139
