# [C] Local Privilege Escalation via Exposed XPC Method Due to Client Verification Failure in stats

## Summary
Severity: Critical
Advisory: CVE-2025-21606
Aliases: GHSA-qwhf-px96-7f6v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-17
Source: https://osv.dev/vulnerability/CVE-2025-21606
Type: osv

## Details
stats is a macOS system monitor in for the menu bar. The Stats application is vulnerable to a local privilege escalation due to the insecure implementation of its XPC service. The application registers a Mach service under the name `eu.exelban.Stats.SMC.Helper`. The associated binary, eu.exelban.Stats.SMC.Helper, is a privileged helper tool designed to execute actions requiring elevated privileges on behalf of the client, such as setting fan modes, adjusting fan speeds, and executing the `powermetrics` command. The root cause of this vulnerability lies in the `shouldAcceptNewConnection` method, which unconditionally returns YES (or true), allowing any XPC client to connect to the service without any form of verification. As a result, unauthorized clients can establish a connection to the Mach service and invoke methods exposed by the HelperTool interface. An attacker can exploit this vulnerability to modify the hardware settings of the user’s device and execute arbitrary code with root privileges. This issue has been addressed in version 2.11.21 and all users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21606.json
- https://github.com/exelban/stats/security/advisories/GHSA-qwhf-px96-7f6v
- https://nvd.nist.gov/vuln/detail/CVE-2025-21606
- https://github.com/exelban/stats/commit/c10759f7a186efdd82ddd818dae2ac1f853691fc
