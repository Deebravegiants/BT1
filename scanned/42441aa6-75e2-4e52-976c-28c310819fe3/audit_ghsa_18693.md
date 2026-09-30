# [H] Docker Compose Vulnerable to Path Traversal via OCI Artifact Layer Annotations

## Summary
Severity: High
Advisory: GHSA-gv8h-7v7w-r22q
CVE: CVE-2025-62725
CWE: CWE-20, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-gv8h-7v7w-r22q
Type: github-advisory

## Affected
- Go: `github.com/docker/compose/v2` — affected >=2.34.0 <2.40.2

## Details
Docker Compose trusts the path information embedded in remote OCI compose artifacts. When a layer includes the annotations com.docker.compose.extends or com.docker.compose.envfile, Compose joins the attacker‑supplied value from com.docker.compose.file/com.docker.compose.envfile with its local cache directory and writes the file there. 

### Impact
This affects any platform or workflow that resolves remote OCI compose artifacts, Docker Desktop, standalone Compose binaries on Linux, CI/CD runners, cloud dev environments is affected.
An attacker can escape the cache directory and overwrite arbitrary files on the machine running docker compose, even if the user only runs read‑only commands such as docker compose config or docker compose ps.

### Patches
v2.40.2

### Workarounds
NA

## References
- https://github.com/docker/compose/security/advisories/GHSA-gv8h-7v7w-r22q
- https://nvd.nist.gov/vuln/detail/CVE-2025-62725
- https://github.com/docker/compose/commit/69bcb962bfb2ea53b41aa925333d356b577d6176
- https://github.com/docker/compose
