# [H] SFTPGo has insufficient sanitization of user provided rsync command

## Summary
Severity: High
Advisory: GHSA-vj7w-3m8c-6vpx
CVE: CVE-2025-24366
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-07
Source: https://github.com/advisories/GHSA-vj7w-3m8c-6vpx
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=0.9.5 <2.6.5
- Go: `github.com/drakkan/sftpgo` — affected >=0

## Details
### Impact
SFTPGo supports execution of a defined set of commands via SSH. Besides a set of default commands some optional commands can be activated, one of them being `rsync`: it is disabled in the default configuration and it is limited to the local filesystem, it does not work with cloud/remote storage backends.

Due to missing sanitization of the client provided `rsync` command, an authenticated remote user can use some options of the rsync command to read or write files with the permissions of the SFTPGo server process. 

### Patches
This issue was fixed in version v2.6.5 by checking the client provided arguments.

https://github.com/drakkan/sftpgo/commit/b347ab6051f6c501da205c09315fe99cd1fa3ba1

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-vj7w-3m8c-6vpx
- https://nvd.nist.gov/vuln/detail/CVE-2025-24366
- https://github.com/drakkan/sftpgo/commit/b347ab6051f6c501da205c09315fe99cd1fa3ba1
- https://github.com/drakkan/sftpgo
