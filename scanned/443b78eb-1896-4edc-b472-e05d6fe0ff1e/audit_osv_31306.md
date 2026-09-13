# [M] macOS Rocket.Chat: TCC Policy Bypass via Dylib Injection Due to Missing Code Signing Flags and Dangerous Entitlements

## Summary
Severity: Medium
Advisory: CVE-2024-8270
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2024-8270
Type: osv

## Details
The macOS Rocket.Chat application is affected by a vulnerability that allows bypassing  Transparency, Consent, and Control (TCC) policies, enabling the exploitation or abuse of permissions specified in its entitlements (e.g., microphone, camera, automation, network client). Since Rocket.Chat was not signed with the Hardened Runtime nor set to enforce Library Validation, it is vulnerable to DYLIB injection attacks, which can lead to unauthorized actions or escalation of permissions. Consequently, an attacker gains capabilities that are not permitted by default under the Sandbox and its application profile.

## References
- https://pentraze.com/
- https://pentraze.com/vulnerability-reports/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8270.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8270
- https://github.com/RocketChat/Rocket.Chat.Electron
