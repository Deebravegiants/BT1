# [H] moby/go-archive: Crafted tar archive can write outside the extraction directory

## Summary
Severity: High
Advisory: GHSA-hfg8-hc9c-6c3h
CVE: CVE-2026-17106
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-hfg8-hc9c-6c3h
Type: github-advisory

## Affected
- Go: `github.com/moby/go-archive` — affected >=0 <0.3.0

## Details
### Summary
The tar extraction routines in `moby/go-archive` (`Unpack`, `UnpackLayer`, `Untar`/`UntarUncompressed`, and the `ApplyLayer` helpers) do not confine filesystem operations to the destination directory. A crafted archive can create or overwrite files **outside** the intended destination. 

### Details
The extractor decides where each archive entry lands using lexical string checks and then performs the filesystem operation on a path that is resolved by the OS, so a links introduced by the archive can be followed out of the destination directory.

### Impact
An attacker who controls the contents of archive can create or overwrite files at arbitrary paths writable by the extracting process.

### Workarounds
Only extract trusted archives.

## References
- https://github.com/moby/go-archive/security/advisories/GHSA-hfg8-hc9c-6c3h
- https://github.com/moby/moby/issues/52948
- https://docs.docker.com/desktop/release-notes/#4860
- https://github.com/bikini/exploitarium/tree/main/docker-cp-copyout-destination-escape
- https://github.com/docker/cli/releases/tag/v29.7.0
- https://github.com/moby/go-archive
- https://github.com/moby/moby/releases/tag/docker-v29.7.0
- https://www.imperva.com/blog/copyescape-taking-over-docker-hosts-with-docker-cp
