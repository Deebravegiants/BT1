# [C] Google-ADK Continuation Forgery

## Summary
Severity: Critical
Advisory: CVE-2026-18236
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-18236
Type: osv

## Details
A vulnerability in the Agent Development Kit (ADK) allows for continuation forgery in tool confirmations. An attacker who is able to manipulate or inject events into the session history can execute unauthorized tools by forging a tool confirmation response. This is possible because the framework did not verify if the target tool was registered to the executing agent, did not validate if the tool actually required confirmation, and did not match the confirmation arguments against the original tool call event in the history.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18236.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18236
- https://github.com/google/adk-python/commit/c03f333769feaeaa9fe8910fbe95cb9f2d513f54
