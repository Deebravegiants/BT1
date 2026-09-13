# [M] SFTPGo allows administrators to restrict command execution from the EventManager

## Summary
Severity: Medium
Advisory: GHSA-49cc-xrjf-9qf7
CVE: CVE-2024-52309
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2024-11-21
Source: https://github.com/advisories/GHSA-49cc-xrjf-9qf7
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.4.0 <2.6.3
- Go: `sftpgo` — affected >=2.4.0 <2.6.3

## Details
### Impact

One powerful feature of SFTPGo is the ability to have the EventManager execute scripts or run applications in response to certain events.
This feature is very common in all software similar to SFTPGo and is generally unrestricted. 

However, any SFTPGo administrator with permission to run a script has access to the underlying OS/container with the same permissions as the user running SFTPGo, so they can access the database and server configurations.

This is unexpected for some SFTPGo administrators who think that there is a clear distinction between accessing the system shell and accessing the SFTPGo WebAdmin UI.

### Patches

To avoid this confusion, running system commands is now disabled by default, and an allow list has been added so that system administrators configuring SFTPGo must explicitly define which commands are allowed to be configured from the WebAdmin UI.

https://github.com/drakkan/sftpgo/commit/88b1850b5806eee81150873d4e565144b21021fb
https://github.com/drakkan/sftpgo/commit/b524da11e9466d05fe03304713ee1c61bb276ec4

### Workarounds

Allow EventManager to be used only by SFTPGo administrators who also have shell access.

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-49cc-xrjf-9qf7
- https://nvd.nist.gov/vuln/detail/CVE-2024-52309
- https://github.com/drakkan/sftpgo/commit/88b1850b5806eee81150873d4e565144b21021fb
- https://github.com/drakkan/sftpgo/commit/b524da11e9466d05fe03304713ee1c61bb276ec4
- https://github.com/drakkan/sftpgo
- https://pkg.go.dev/vuln/GO-2024-3283
