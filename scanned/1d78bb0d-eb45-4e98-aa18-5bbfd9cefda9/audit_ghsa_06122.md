# [H] SSH.NET: ScpClient Recursive Download Allows Arbitrary File Write via Server-Controlled SCP Filenames

## Summary
Severity: High
Advisory: GHSA-q939-rpr3-3284
CVE: CVE-2026-48798
CWE: CWE-22, CWE-73
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-q939-rpr3-3284
Type: github-advisory

## Affected
- NuGet: `SSH.NET` — affected >=0 <2026.0.0

## Details
## Summary

`ScpClient.Download(string directoryName, DirectoryInfo directoryInfo)` writes files and directories using names returned by the remote SCP server during recursive downloads, with no validation that the resulting path stays inside the requested local directory. A malicious, compromised, or man-in-the-middle SCP server can return names containing `../` sequences (or absolute paths), causing the client to create directories and write/overwrite files anywhere the client process has access. This is similar to OpenSSH [CVE-2019-6111](https://github.com/advisories/GHSA-jr78-hfw4-xp7g), but with directory traversal capability.

## Impact

A malicious/compromised/MITM SCP server can create or write files outside the intended download directory, anywhere the client process can write. Overwriting files such as ~/.ssh/authorized_keys, shell rc files, cron entries, or application binaries/config can lead to persistence, privilege escalation, or remote code execution on the client host. Requires the victim to perform a directory download from the attacker-controlled server.

## Remediation

The fixed release ensures that remotely-supplied file and directory names are valid local names such that the constructed local path is contained within the given local directory, and throws `ScpException` when an invalid name is detected.

[600be0de543765995a189b5d7cd4efac5007f3ce](https://github.com/sshnet/SSH.NET/commit/600be0de543765995a189b5d7cd4efac5007f3ce)

## References
- https://github.com/sshnet/SSH.NET/security/advisories/GHSA-q939-rpr3-3284
- https://nvd.nist.gov/vuln/detail/CVE-2026-48798
- https://github.com/sshnet/SSH.NET/commit/600be0de543765995a189b5d7cd4efac5007f3ce
- https://github.com/sshnet/SSH.NET
- https://github.com/sshnet/SSH.NET/releases/tag/2026.0.0
