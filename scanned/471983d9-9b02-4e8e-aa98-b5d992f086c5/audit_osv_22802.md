# [H] Mist vulnerable to user providing a Sudo binary for authentication checks

## Summary
Severity: High
Advisory: CVE-2022-39245
Aliases: GHSA-pxg4-7c7r-2ww6
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-26
Source: https://osv.dev/vulnerability/CVE-2022-39245
Type: osv

## Details
Mist is the command-line interface for the makedeb Package Repository. Prior to version 0.9.5, a user-provided `sudo` binary via the `PATH` variable can allow a local user to run arbitrary commands on the user's system with root permissions. Versions 0.9.5 and later contain a patch. No known workarounds exist.

## References
- https://github.com/makedeb/mist/releases/tag/v0.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39245.json
- https://github.com/makedeb/mist/security/advisories/GHSA-pxg4-7c7r-2ww6
- https://nvd.nist.gov/vuln/detail/CVE-2022-39245
- https://github.com/makedeb/mist/commit/e257561a32cffe3c541b265097959adaea3d6b67
