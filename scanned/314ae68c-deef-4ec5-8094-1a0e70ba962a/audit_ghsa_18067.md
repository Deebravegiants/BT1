# [C] m00nl1ght-dev/steam-workshop-deploy: Exposure of Version-Control Repository to an Unauthorized Control Sphere and Insufficiently Protected Credentials

## Summary
Severity: Critical
Advisory: GHSA-x6gv-2rvh-qmp6
CWE: CWE-212, CWE-522, CWE-527
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-08-13
Source: https://github.com/advisories/GHSA-x6gv-2rvh-qmp6
Type: github-advisory

## Affected
- GitHub Actions: `m00nl1ght-dev/steam-workshop-deploy` — affected >=0 <4
- GitHub Actions: `BoldestDungeon/steam-workshop-deploy` — affected >=0 <2.0.0

## Details
## Summary
The `steam-workshop-deploy` github action does not exclude the `.git` directory when packaging content for deployment and provides no built-in way to do so. If a `.git` folder exists in the target directory (e.g., due to a local Git repo, custom project structure, or via  the `actions/checkout` workflow), it is silently included in the output package. This results in leakage of sensitive repository metadata and potentially credentials, including github personal access tokens (PATs) embedded in `.git/config`.

Many game modding projects require packaging from the project root as the game expects certain files (assets, configuration, metadata) to be present at specific root-level paths. Consequently, the `.git` directory often exists alongside these required files and gets packaged unintentionally, especially when using `actions/checkout`.

While github hosted runners automatically revoke ephemeral credentials at the end of each job, the severity of this issue increases dramatically in other CI environments:

- Self-hosted runners may store long-lived tokens or secrets.
- Developers may maintain their own `.git` folders with embedded PATs or remotes tied to private repositories.
- The workflow may run without the `actions/checkout` action, distributing the `.git` directory present on the running machine if it exists in the directory.

A real example of an affected mod can be found here: https://github.com/BoldestDungeon/wildermyth-drauven-pcs/security/advisories/GHSA-7j9v-72w9-ww6w

## Details
Who is affected:
- Any user of `steam-workshop-deploy` operating in an environment where `.git` exists in the packaging directory.
- Any user of `steam-workshop-deploy` operating in an environment where the [actions/checkout](https://github.com/actions/checkout) workflow is used and then the `.git` directory is inadvertently generated within the packaging directory (greatly reduced severity due to the ephemeral nature of github actions).

## Impact
The severity of this issue for downstream components can range from **0.0** (no credentials, sensitive metadata, or private source code were present in the packaging directory) to **10.0** (extremely sensitive, high privilige credentials or source code from private repositories were exposed).

The actual severity depends primarily on the permissions, scope, and nature of the exposed data:
* **Low/none (0.0-3.9)**: Only non-sensitive repository metadata was exposed, no credentials were present, or only public facing code was included.
* **Medium(4.0-6.9)**: Credentials with limited repository access and/or short lifespan (e.g., ephemeral tokens) were exposed, or non-sensitive private code was disclosed.
* **High/critical (7.0-10.0)**: Long-lived tokens, organization-wide credentials, or credentials with administrative privileges were exposed, potentially enabling full repository compromise, secret extraction, code tampering, or the complete leak of private repository source code.

As such, each downstream consumer should independently assess their exposure by reviewing packaged artifacts for the presence of `.git` directories or other credentials, and evaluating both the sensitivity of any credentials found and the confidentiality of any included source code.

Consequences may include:
  - Unauthorized access to git repositories via exposed PATs.
  - Tampering with repository code or metadata.
  - Malicious CI behavior (triggering workflows, reading secrets).
  - Disclosure of commit history, remote origins, or other sensitive internal structure.

## Recommendation
This issue should be considered **severe** due to the potential exposure of sensitive tokens and repository metadata. Although most workflows that use `steam-workshop-deploy` also employ `actions/checkout`, which handles tokens and credentials more securely, there are legitimate use cases where `actions/checkout` is not used or where custom `.git` folders exist. Additionally, `actions/checkout` can accept a on-emphemeral tokens as a parameter for its workflow. In such cases, long-lived or sensitive credentials may be packaged and exposed, greatly increasing the risk of unauthorized access and repository compromise.  Therefore, this issue should be considered severe regardless of common usage patterns.

**Downstream:**
- Downstream components should revoke any credentials or PATs associated with workflows or repositories that use this github action

**This Deployment Action**

- [x] The action should exclude `.git/` and other common sensitive file(s) by default from all packaging operations.
- [x] A `deployignore` or similar mechanism should be introduced to give users finer control of what files or directories are included for deployed artifacts

## References
- https://github.com/BoldestDungeon/steam-workshop-deploy/security/advisories/GHSA-x6gv-2rvh-qmp6
- https://github.com/BoldestDungeon/steam-workshop-deploy/commit/0ba85729da32108e1cc498d1b3d6760857b5c04d
- https://github.com/m00nl1ght-dev/steam-workshop-deploy/commit/913f0844e2153d798189397036918f4ceb0911e0
- https://github.com/BoldestDungeon/steam-workshop-deploy
- https://github.com/BoldestDungeon/steam-workshop-deploy/releases/tag/V2.0.0
- https://github.com/m00nl1ght-dev/steam-workshop-deploy/releases/tag/v4
