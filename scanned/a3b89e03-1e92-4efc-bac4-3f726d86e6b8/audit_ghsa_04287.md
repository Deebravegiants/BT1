# [M] Pi Agent: Pi loads project-local extensions without approval

## Summary
Severity: Medium
Advisory: GHSA-mqxh-6gq7-558m
CVE: CVE-2026-54325
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-mqxh-6gq7-558m
Type: github-advisory

## Affected
- npm: `@earendil-works/pi-coding-agent` — affected >=0 <0.79.0

## Details
# Pi loads project-local extensions without approval

Pi before 0.79.0 loaded project-local configuration and resources from a repository's `.pi` directory without first asking the user to trust that repository. This included project-local extensions, which are executable TypeScript or JavaScript modules loaded into the Pi process.

An attacker who controls a repository could place Pi-specific project resources in that repository. If a user then started Pi from that working tree, the project-local extension code could run with the same privileges as the local Pi process without the user having a convenient way to make a trust decision.

## Info

The affected component is Pi's project resource loading path. Before 0.79.0, startup loaded project `.pi/settings.json`, auto-discovered `.pi` resources, project package-managed resources, and project instruction files as part of normal session initialization. Project-local extensions were included in the same extension set as user/global extensions and were initialized before there was a project trust boundary.

Extensions like pi itself are not sandboxed. They run in the Pi process and can register commands, tools, and event handlers. The vulnerable behavior was not a privilege escalation across an operating-system boundary, but it allowed repository-controlled Pi extension code to execute implicitly when a user ran Pi in that repository.

## Impact

Exploitation requires user interaction: the attacker must get a user to open or otherwise work in an attacker-controlled repository and start Pi there. The attacker does not need an account on the user's machine or prior privileges in Pi.

If exploited, project-local extension code runs with the same permissions as the user running Pi. It can access files, environment variables, credentials available to the process, the network, and local tools available to that user. In CVSS terms, this advisory rates the impact as limited confidentiality and integrity impact without a distinct availability impact because exploitation requires local user action in an untrusted repository and does not cross a privilege boundary.

This risk is most relevant for users who run Pi in repositories they have not reviewed or do not trust. Pi's security guidance requires users to trust the codebases they work with, or to use an external sandbox or isolation boundary for untrusted repositories.

## Affected versions

- Affected: `< 0.79.0`
- Patched: `0.79.0`

## The solution

Pi 0.79.0 added project trust gating for project-local inputs. On interactive startup, Pi now asks before loading project-local settings, instructions, resources, package-managed resources, or extensions when a trust decision has not already been saved for the working directory.

Non-interactive modes do not prompt. Without a saved trust decision, they ignore project-local inputs unless `--approve` or `-a` is passed. Users can also pass `--no-approve` or `-na` to ignore project-local inputs for a single run even when a project is already trusted.

Before trust is resolved, Pi loads only user/global extensions and extensions passed explicitly on the command line. Those extensions can participate in the `project_trust` event; project-local extensions are not loaded until after the project is trusted.

## Recommendations

Upgrade `@earendil-works/pi-coding-agent` to version 0.79.0 or later.

After upgrading, review project trust prompts carefully and only trust repositories whose Pi-specific configuration and extensions you are willing to run. The upgrade makes this trust decision explicit, but it does not change Pi's security model: users should work only in trusted repositories, or use external isolation for untrusted code. Use `--no-approve` for one-off runs where project-local inputs should be ignored. For untrusted repositories or unattended automation, follow Pi's [security guidance](https://pi.dev/docs/latest/security) and run Pi inside an operating-system sandbox, container, VM, or other isolation boundary with only the files and credentials required for the task.

## Workarounds

Before and after this change, Pi users should only run Pi in repositories they trust, or in an external sandbox or isolation boundary when working with untrusted code. Pi 0.79.0 adds an explicit trust prompt as a defense-in-depth and user-safety improvement; it is not a sandbox and it does not make untrusted repositories safe.

If upgrading is not possible and your workflow already enforces this trust boundary, continue to avoid running Pi directly in untrusted repositories. Inspect and remove project-local Pi configuration and resources before use, especially project-local extensions and package configuration. Disabling extensions and other project resources with command-line flags can reduce exposure, but trusted or isolated execution remains the primary mitigation.

## Timeline

- 2026-05-25: Report received.
- 2026-06-05: Project trust gating committed.
- 2026-06-08: Project trust refinements and security model documentation completed.
- 2026-06-08: Fixed version 0.79.0 released.
- 2026-06-08: Advisory published.

## Credits

Reported by [@qerogram](https://github.com/qerogram), [@urianpaul94](https://github.com/urianpaul94), [@EQSTLab](https://github.com/EQSTLab), and [@kamalmarhubi](https://github.com/kamalmarhubi).

## References
- https://github.com/earendil-works/pi/security/advisories/GHSA-mqxh-6gq7-558m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54325
- https://github.com/earendil-works/pi/commit/38f18be44727e669eb0a6e2eb8edb51b0232d83c
- https://github.com/earendil-works/pi/commit/718215bd95b6fc6fa251580d27ea8aab857de390
- https://github.com/earendil-works/pi/commit/89a92207f1c9303d53d822fd9b0ac21578834cb4
- https://github.com/earendil-works/pi/commit/ce3a72444e1cc1eaa50475fb3378c7ffbb53ef49
- https://github.com/earendil-works/pi/commit/ff3e9df5f5b32368c20b0ef553a6834b3dee9350
- https://github.com/earendil-works/pi
- https://github.com/earendil-works/pi/releases/tag/v0.79.0
