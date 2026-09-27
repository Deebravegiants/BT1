# [H] Artifact Hub arbitrary file read vulnerability

## Summary
Severity: High
Advisory: GHSA-hmq4-c2r4-5q8h
CVE: CVE-2023-45823
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-hmq4-c2r4-5q8h
Type: github-advisory

## Affected
- Go: `github.com/artifacthub/hub` — affected >=0 <1.16.0

## Details
### Impact

During a security audit of Artifact Hub's code base, a security researcher at [OffSec](https://www.offsec.com/) identified a bug in which by using symbolic links in certain kinds of repositories loaded into Artifact Hub, it was possible to read internal files.

Artifact Hub indexes content from a variety of sources, including git repositories. When processing git based repositories, Artifact Hub clones the repository and, depending on the artifact kind, reads some files from it. During this process, in some cases, no validation was done to check if the file was a symbolic link. This made possible to read arbitrary files in the system, potentially leaking sensitive information.

### Patches

This issue has been resolved in version [1.16.0](https://artifacthub.io/packages/helm/artifact-hub/artifact-hub?modal=changelog&version=1.16.0).

## References
- https://github.com/artifacthub/hub/security/advisories/GHSA-hmq4-c2r4-5q8h
- https://nvd.nist.gov/vuln/detail/CVE-2023-45823
- https://artifacthub.io/packages/helm/artifact-hub/artifact-hub?modal=changelog&version=1.16.0
- https://github.com/artifacthub/hub
