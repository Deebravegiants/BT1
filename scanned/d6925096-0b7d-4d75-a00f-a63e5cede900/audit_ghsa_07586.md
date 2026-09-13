# [H] Pterodactyl Panel's SFTP sessions remain active after user account deletion or password change

## Summary
Severity: High
Advisory: GHSA-hr7j-63v7-vj7g
CWE: CWE-284, CWE-613
Ecosystem: Go, Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-hr7j-63v7-vj7g
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.1
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.12.1

## Details
### Summary
Deleting a user account with SFTP access or changing the user's password does not immediately terminate existing SFTP sessions, allowing continued filesystem access after credentials are revoked.
This can result in unintended and unauthorized access to server files even after administrators believe access has been fully invalidated.


### Details
When a user with SFTP access is deleted from the Pterodactyl Panel or when the user's password is changed while one or more SFTP connections are active, those existing connections remain fully functional.

Neither account deletion nor password change invalidates the authentication state of already-established SFTP sessions. As a result, the active SFTP connection pool continues to allow read and write operations until the client disconnects or the session times out.

This behavior occurs even when the password is changed by an administrator through the panel, meaning credential rotation does not revoke active access.

This suggests that active SFTP sessions are not tracked or forcefully terminated on credential revocation events. This effectively prevents administrators from responding to credential compromise incidents in real time.


### PoC
Scenario 1: Account deletion
1. Create a user with SFTP access to a server.
2. Connect to the server via SFTP using any SFTP client (e.g. sftp, FileZilla).
3. Keep the SFTP session open and active.
4. Delete the user account from the Pterodactyl Panel.
5. Continue performing file operations through the already-established SFTP connection.

Result:
The SFTP session remains active and usable despite the user account being deleted.

Scenario 2: Password change
1. Create a user with SFTP access to a server.
2. Establish an active SFTP connection.
3. Change the user's password (including via administrator panel).
4. Continue performing file operations using the existing SFTP connection.

Result:
The SFTP session remains active and usable even after the password has been changed.


### Impact
This issue prevents immediate revocation of compromised credentials. Vulnerability type: Access control / session invalidation issue

Impacted parties:

1. Server administrators
2. Hosting providers using Pterodactyl Panel

Security impact:

Deleted users may retain filesystem access longer than intended, which can lead to:

1. Unauthorized data access
2. Data modification or deletion
3. Compliance and security policy violations

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-hr7j-63v7-vj7g
- https://github.com/pterodactyl/panel/commit/0e74f3aadec89405751ec602c77fc1d030a417c0
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.12.1
