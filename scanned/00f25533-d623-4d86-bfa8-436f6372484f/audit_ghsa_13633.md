# [M] Artifact Hub has Incorrect Docker Hub registry check

## Summary
Severity: Medium
Advisory: GHSA-g6pq-x539-7w4j
CVE: CVE-2023-45821
CWE: CWE-494
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-g6pq-x539-7w4j
Type: github-advisory

## Affected
- Go: `github.com/artifacthub/hub` — affected >=0 <1.16.0

## Details
### Impact

During a security audit of Artifact Hub's code base, a security researcher at [OffSec](https://www.offsec.com/) identified a bug in which the `registryIsDockerHub` function was only checking that the registry domain had the `docker.io` suffix.

Artifact Hub allows providing some Docker credentials that are used to increase the rate limit applied when interacting with the Docker Hub registry API to read publicly available content. Due to the incorrect check described above, it'd be possible to hijack those credentials by purchasing a domain which ends with `docker.io` and deploying a fake OCI registry on it.

<https://artifacthub.io/> uses some credentials that only have permissions to read public content available in the Docker Hub. However, even though credentials for private repositories (disabled on `artifacthub.io`) are handled in a different way, other Artifact Hub deployments could have been using them for a different purpose.

### Patches

This issue has been resolved in version [1.16.0](https://artifacthub.io/packages/helm/artifact-hub/artifact-hub?modal=changelog&version=1.16.0).

## References
- https://github.com/artifacthub/hub/security/advisories/GHSA-g6pq-x539-7w4j
- https://nvd.nist.gov/vuln/detail/CVE-2023-45821
- https://artifacthub.io/packages/helm/artifact-hub/artifact-hub?modal=changelog&version=1.16.0
- https://github.com/artifacthub/hub
