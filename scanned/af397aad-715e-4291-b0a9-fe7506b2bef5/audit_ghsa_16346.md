# [M] Classic builder cache poisoning

## Summary
Severity: Medium
Advisory: GHSA-xw73-rw38-6vjc
CVE: CVE-2024-24557
CWE: CWE-345, CWE-346
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-xw73-rw38-6vjc
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <24.0.9
- Go: `github.com/moby/moby` — affected >=0 <24.0.9
- Go: `github.com/moby/moby` — affected >=25.0.0 <25.0.2
- Go: `github.com/docker/docker` — affected >=25.0.0 <25.0.2

## Details
The classic builder cache system is prone to cache poisoning if the image is built `FROM scratch`.
Also, changes to some instructions (most important being `HEALTHCHECK` and `ONBUILD`) would not cause a cache miss.


An attacker with the knowledge of the Dockerfile someone is using could poison their cache by making them pull a specially crafted image that would be considered as a valid cache candidate for some build steps.

For example, an attacker could create an image that is considered as a valid cache candidate for:
```
FROM scratch
MAINTAINER Pawel
```

when in fact the malicious image used as a cache would be an image built from a different Dockerfile.

In the second case, the attacker could for example substitute a different `HEALTCHECK` command.


### Impact

23.0+ users are only affected if they explicitly opted out of Buildkit (`DOCKER_BUILDKIT=0` environment variable) or are using the `/build` API endpoint (which uses the classic builder by default).

All users on versions older than 23.0 could be impacted. An example could be a CI with a shared cache, or just a regular Docker user pulling a malicious image due to misspelling/typosquatting.

Image build API endpoint (`/build`) and `ImageBuild` function from `github.com/docker/docker/client` is also affected as it the uses classic builder by default. 


### Patches

Patches are included in Moby releases:

- v25.0.2
- v24.0.9
- v23.0.10

### Workarounds

- Use `--no-cache` or use Buildkit if possible (`DOCKER_BUILDKIT=1`, it's default on 23.0+ assuming that the buildx plugin is installed).
- Use `Version = types.BuilderBuildKit` or `NoCache = true` in `ImageBuildOptions` for `ImageBuild` call.

## References
- https://github.com/moby/moby/security/advisories/GHSA-xw73-rw38-6vjc
- https://nvd.nist.gov/vuln/detail/CVE-2024-24557
- https://github.com/moby/moby/commit/3e230cfdcc989dc524882f6579f9e0dac77400ae
- https://github.com/moby/moby/commit/fca702de7f71362c8d103073c7e4a1d0a467fadd
- https://github.com/moby/moby/commit/fce6e0ca9bc000888de3daa157af14fa41fcd0ff
- https://github.com/moby/moby
