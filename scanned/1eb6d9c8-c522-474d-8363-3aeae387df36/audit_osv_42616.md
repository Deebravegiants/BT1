# [C] Livebook Teams identity check fails open when the deployment group is unresolvable, allowing unauthenticated access

## Summary
Severity: Critical
Advisory: CVE-2026-68746
Aliases: EEF-CVE-2026-68746, GHSA-74j5-6grg-g6wj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-68746
Type: osv

## Details
Not Failing Securely ('Failing Open') vulnerability in livebook-dev livebook allows an unauthenticated network client to obtain full access to a Livebook server that enforces identity through Livebook Teams.

A Livebook Agent or App Server connected to Livebook Teams caches the identifier of the deployment group it belongs to, and resolves that identifier against a locally cached list of deployment groups on every request in order to decide whether Teams identity enforcement is active. Livebook.Hubs.TeamClient.handle_call/3 in lib/livebook/hubs/team_client.ex does not distinguish a deployment group that could not be resolved from one that was resolved with identity enforcement switched off: the clause matches only the case where a group was found with enforcement enabled, and falls through to a catch-all that reports enforcement as switched off for everything else. The two neighbouring functions that decide user and application access resolve the same identifier and treat the same unresolved result as a denial.

When the identity status is reported as switched off, Livebook.ZTA.LivebookTeams.authenticate/3 in lib/livebook/zta/livebook_teams.ex returns empty identity metadata and allows the request to continue instead of halting it. LivebookWeb.UserPlug.build_current_user/3 merges that empty metadata into a newly built user, whose access type defaults to full access, and LivebookWeb.AuthPlug.authorized?/1 grants access to any user holding full access.

The cached identifier becomes unresolvable when the deployment group it refers to is deleted while the agent is not connected to receive the change, most concretely when a deployment group is deleted during the window in which an agent is disconnected or reconnecting. The client removes the group from its cached list without clearing the identifier that refers to it. Any client able to reach the affected server over the network is then granted the same access as a fully privileged member of the organisation, including the ability to read notebooks and configured secrets, execute code on the server's runtime, and disrupt its operation.

This issue affects livebook: from 0.19.7 before 0.19.9.

## References
- https://cna.erlef.org/cves/CVE-2026-68746.html
- https://ghcr.io
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-68746
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68746.json
- https://github.com/livebook-dev/livebook/security/advisories/GHSA-74j5-6grg-g6wj
- https://nvd.nist.gov/vuln/detail/CVE-2026-68746
- https://github.com/livebook-dev/livebook/commit/2d3a2c710c880abd24a2bc888d3cf5239d98cf72
- https://github.com/livebook-dev/livebook/commit/d374e90647edbb00286bfee9182c0161d29a8e07
- https://github.com/livebook-dev/livebook/commit/d6d0dfa746b172540442852f74de4a9deacc433b
- https://github.com/livebook-dev/livebook
