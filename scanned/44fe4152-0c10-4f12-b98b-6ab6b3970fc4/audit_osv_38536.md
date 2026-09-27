# [C] OpenHarness Remote Administrative Command Injection via Gateway Handler

## Summary
Severity: Critical
Advisory: CVE-2026-40502
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-40502
Type: osv

## Details
OpenHarness prior to commit dd1d235 contains a command injection vulnerability that allows remote gateway users with chat access to invoke sensitive administrative commands by exploiting insufficient distinction between local-only and remote-safe commands in the gateway handler. Attackers can execute administrative commands such as /permissions full_auto through remote chat sessions to change permission modes of a running OpenHarness instance without operator authorization.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40502.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40502
- https://www.vulncheck.com/advisories/openharness-remote-administrative-command-injection-via-gateway-handler
- https://github.com/HKUDS/OpenHarness/pull/127
- https://github.com/HKUDS/OpenHarness/commit/dd1d235450dd987b20bff01b7bfb02fe8620a0af
- https://github.com/HKUDS/OpenHarness
