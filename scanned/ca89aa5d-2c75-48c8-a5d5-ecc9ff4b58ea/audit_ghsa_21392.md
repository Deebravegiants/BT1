# [H] Docker Command Escaping in the GitHub Actions Runner

## Summary
Severity: High
Advisory: GHSA-2c6m-6gqh-6qg3
CVE: CVE-2022-39321
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-25
Source: https://github.com/advisories/GHSA-2c6m-6gqh-6qg3
Type: github-advisory

## Affected
- GitHub Actions: `actions/runner` — affected >=2.294.0 <2.296.2
- GitHub Actions: `actions/runner` — affected >=2.290.0 <2.293.1
- GitHub Actions: `actions/runner` — affected >=2.286.0 <2.289.4
- GitHub Actions: `actions/runner` — affected >=2.284.0 <2.285.2
- GitHub Actions: `actions/runner` — affected >=0 <2.283.4

## Details
### Impact

The actions runner invokes the docker cli directly in order to run job containers, service containers, or container actions. A bug in the logic for how the environment is encoded into these docker commands was discovered that allows an input to escape the environment variable and modify that docker command invocation directly. Jobs that use [container actions](https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action), [job containers](https://docs.github.com/en/actions/using-jobs/running-jobs-in-a-container), or [service containers](https://docs.github.com/en/actions/using-containerized-services/about-service-containers) alongside untrusted user inputs in environment variables may be vulnerable.

### Patches
The Actions Runner has been patched, both on `github.com` and hotfixes for GHES and GHAE customers. Please update to one of the following versions of the runner:
- 2.296.2
- 2.293.1
- 2.289.4
- 2.285.2
- 2.283.4

GHES and GHAE customers may want to patch their instance in order to have their runners automatically upgrade to these new runner versions.

### Workarounds
You may want to consider removing any container actions, job containers, or service containers from your jobs until you are able to upgrade your runner versions.


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the actions runner](https://github.com/actions/runner)

## References
- https://github.com/actions/runner/security/advisories/GHSA-2c6m-6gqh-6qg3
- https://nvd.nist.gov/vuln/detail/CVE-2022-39321
- https://github.com/actions/runner/pull/2107
- https://github.com/actions/runner/pull/2108
- https://github.com/actions/runner
