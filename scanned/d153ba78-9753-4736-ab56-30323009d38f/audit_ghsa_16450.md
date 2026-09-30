# [H] dotmesh arbitrary file read and/or write

## Summary
Severity: High
Advisory: GHSA-hf54-fq2m-p9v6
CVE: CVE-2020-26312
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-hf54-fq2m-p9v6
Type: github-advisory

## Affected
- Go: `github.com/dotmesh-io/dotmesh` — affected >=0

## Details
Dotmesh is a git-like command-line interface for capturing, organizing and sharing application states. In versions 0.8.1 and prior, the unsafe handling of symbolic links in an unpacking routine may enable attackers to read and/or write to arbitrary locations outside the designated target folder. The routine `untarFile` attempts to guard against creating symbolic links that point outside the directory a tar archive is extracted to. However, a malicious tarball first linking `subdir/parent` to `..` (allowed, because `subdir/..` falls within the archive root) and then linking `subdir/parent/escapes` to `..` results in a symbolic link pointing to the tarball’s parent directory, contrary to the routine’s goals. This issue may lead to arbitrary file write (with same permissions as the program running the unpack operation) if the attacker can control the archive file. Additionally, if the attacker has read access to the unpacked files, they may be able to read arbitrary system files the parent process has permissions to read. As of time of publication, no patch for this issue is available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26312
- https://github.com/dotmesh-io/dotmesh
- https://github.com/dotmesh-io/dotmesh/blob/master/pkg/archiver/tar.go#L255
- https://securitylab.github.com/advisories/GHSL-2020-254-zipslip-dotmesh
