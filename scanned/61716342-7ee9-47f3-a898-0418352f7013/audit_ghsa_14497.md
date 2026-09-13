# [M] Buildkit credentials inlined to Git URLs could end up in provenance attestation

## Summary
Severity: Medium
Advisory: GHSA-gc89-7gcr-jxqc
CVE: CVE-2023-26054
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-gc89-7gcr-jxqc
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0.10.0 <0.11.4

## Details
When the user sends a build request that contains a Git URL that contains credentials and the build creates a provenance attestation describing that build, these credentials could be visible from the provenance attestation.

Git URL can be passed in two ways:

1) Invoking build directly from a URL with credentials.

```
buildctl build --frontend dockerfile.v0 --context https://<credentials>@url/repo.git
```

Equivalent in `docker buildx` would be

```
docker buildx build https://<credentials>@url/repo.git
```

2) If the client sends additional VCS info hint parameters on builds from a local source. Usually, that would mean reading the origin URL from `.git/config` file. 

Thanks to Oscar Alberto Tovar for discovering the issue.

### Impact
When a build is performed under specific conditions where credentials were passed to BuildKit they may be visible to everyone who has access to provenance attestation.

Provenance attestations and VCS info hints were added in version v0.11.0. Previous versions are not vulnerable.

In v0.10, when building directly from Git URL, the same URL could be visible in `BuildInfo` structure that is a predecessor of Provenance attestations. Previous versions are not vulnerable.

Note: [Docker Build-push Github action](https://github.com/docker/build-push-action) builds from Git URLs by default but **is not** affected by this issue even when working with private repositories because the credentials are passed [with build secrets](https://github.com/docker/build-push-action/blob/v4.0.0/src/context.ts#L203) and not with URLs.

### Patches
Bug is fixed in v0.11.4 . 

### Workarounds
It is recommended to pass credentials with build secrets when building directly from Git URL as a more secure alternative than modifying the URL.

In Docker Buildx, VCS info hint can be disabled by setting `BUILDX_GIT_INFO=0`. `buildctl` does not set VCS hints based on `.git` directory, and values would need to be passed manually with `--opt`.


### References
- Inline credentials in URLs deprecated in RFC3986 https://www.rfc-editor.org/rfc/rfc3986#section-3.2.1

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-gc89-7gcr-jxqc
- https://nvd.nist.gov/vuln/detail/CVE-2023-26054
- https://github.com/moby/buildkit/commit/75123c696506bdbca1ed69906479e200f1b62604
- https://github.com/moby/buildkit
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYZOKMMVX4SIEHPJW3SJUQGMO5YZCPHC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XNF4OLYZRQE75EB5TW5N42FSXHBXGWFE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTE4ITXXPIWZEQ4HYQCB6N6GZIMWXDAI
- https://www.rfc-editor.org/rfc/rfc3986#section-3.2.1
