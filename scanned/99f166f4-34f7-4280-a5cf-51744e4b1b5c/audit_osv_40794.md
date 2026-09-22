# [M] Microsoft UFO: COMMAND_RESULTS handler creates unowned sessions, allowing authenticated session-squatting denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-55440
Aliases: GHSA-hxjv-fmjf-wmjf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-55440
Type: osv

## Details
Microsoft UFO open-source framework for intelligent automation across devices and platforms. Prior to 3.0.7, the COMMAND_RESULTS handler in ufo/server/ws/handler.py called get_or_create_session in ufo/server/services/session_manager.py without owner_client_id, allowing an authenticated client to create an unowned attacker-chosen session_id such as constellation_task_id = f"{task_name}@{task_id}" and deny the legitimate owner or exhaust memory with phantom sessions. This issue is fixed in version 3.0.7.

## References
- https://github.com/microsoft/UFO/releases/tag/3.0.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55440.json
- https://github.com/microsoft/UFO/security/advisories/GHSA-hxjv-fmjf-wmjf
- https://nvd.nist.gov/vuln/detail/CVE-2026-55440
- https://github.com/microsoft/UFO/commit/cc653bde75337ab60c320e6b7cb61b86ba6ca948
