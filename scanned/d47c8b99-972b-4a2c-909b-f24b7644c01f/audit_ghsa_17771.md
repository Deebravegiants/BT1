# [H] Git LFS permits exfiltration of credentials via crafted HTTP URLs

## Summary
Severity: High
Advisory: GHSA-q6r2-x2cc-vrp7
CVE: CVE-2024-53263
CWE: CWE-436, CWE-74
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-q6r2-x2cc-vrp7
Type: github-advisory

## Affected
- Go: `github.com/git-lfs/git-lfs` — affected >=0.1.0
- Go: `github.com/git-lfs/git-lfs/v3` — affected >=3.0.0 <3.6.1

## Details
### Impact

When Git LFS requests credentials from Git for a remote host, it passes portions of the host's URL to the `git-credential(1)` command without checking for embedded line-ending control characters, and then sends any credentials it receives back from the Git credential helper to the remote host.  By inserting URL-encoded control characters such as line feed (LF) or carriage return (CR) characters into the URL, an attacker may be able to retrieve a user's Git credentials.

### Patches

This problem exists in all previous versions and is patched in v3.6.1.  All users should upgrade to v3.6.1.

### Workarounds

There are no workarounds known at this time.

### References

* https://github.com/git-lfs/git-lfs/security/advisories/GHSA-q6r2-x2cc-vrp7
* https://nvd.nist.gov/vuln/detail/CVE-2024-53263
* https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-53263
* https://github.com/git-lfs/git-lfs/releases/tag/v3.6.1
* [git-lfs/git-lfs@0345b6f816](https://github.com/git-lfs/git-lfs/commit/0345b6f816e611d050c0df67b61f0022916a1c90)

### For more information

If you have any questions or comments about this advisory:
* For general questions, start a discussion in the Git LFS [discussion forum](https://github.com/git-lfs/git-lfs/discussions).
* For reports of additional vulnerabilities, please follow the Git LFS [security reporting policy](https://github.com/git-lfs/git-lfs/blob/main/SECURITY.md).

## References
- https://github.com/git-lfs/git-lfs/security/advisories/GHSA-q6r2-x2cc-vrp7
- https://nvd.nist.gov/vuln/detail/CVE-2024-53263
- https://github.com/git-lfs/git-lfs/commit/0345b6f816e611d050c0df67b61f0022916a1c90
- https://github.com/git-lfs/git-lfs
- https://github.com/git-lfs/git-lfs/releases/tag/v3.6.1
- https://lists.debian.org/debian-lts-announce/2025/01/msg00022.html
- https://pkg.go.dev/vuln/GO-2025-3390
