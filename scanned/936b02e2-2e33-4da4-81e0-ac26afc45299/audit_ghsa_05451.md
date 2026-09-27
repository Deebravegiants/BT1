# [H] Pterodactyl endlessly reprocesses/reuploads activity log data due to SQLite max parameters limit not being considered

## Summary
Severity: High
Advisory: GHSA-2497-gp99-2m74
CVE: CVE-2026-21696
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-2497-gp99-2m74
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=1.7.0 <1.12.0

## Details
### Summary 
Wings does not consider SQLite max parameter limit when processing activity log entries allowing for low privileged user to trigger a condition that floods the panel with activity records 

### Details 
After wings sends activity logs to the panel it deletes the processed activity entries from the wings SQLite database. However, it does not consider the max parameter limit of SQLite, 32766 as of SQLite 3.32.0. 

If wings attempts to delete more than 32766 entries from the SQLite database in one query, it triggers an error (SQL logic error: too many SQL variables (1)) and does not remove any entries from the database. These entries are then indefinitely re-processed and resent to the panel each time the cron runs. 

https://github.com/pterodactyl/wings/blob/9ffbcdcdb1163da823cf9959b9602df9f7dcb54a/internal/cron/activity_cron.go#L81
https://github.com/pterodactyl/wings/blob/9ffbcdcdb1163da823cf9959b9602df9f7dcb54a/internal/cron/sftp_cron.go#L86

### PoC 
Any method that can create the required 32767+ activity entries can trigger this vulnerability. It can (and has) been triggered by normal (non-malicious) use. I attached a simple PoC I used while verifying this that uses sftp to quickly create many small files, thus creating activity entries in the SQLite database. 
https://ptero.co/mococesoca.go


  

### Impact 
By successfully exploiting this vulnerability you can trigger a situation where wings will keep uploading the same activity data to the panel repeatedly (growing each time to include new activity) until the panels’ database server runs out of disk space.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-2497-gp99-2m74
- https://nvd.nist.gov/vuln/detail/CVE-2026-21696
- https://github.com/pterodactyl/panel/commit/09caa0d4995bd924b53b9a9e9b4883ac27bd5607
- https://github.com/pterodactyl/panel/releases/tag/v1.12.0
- https://github.com/pterodactyl/wings
- https://github.com/pterodactyl/wings/blob/9ffbcdcdb1163da823cf9959b9602df9f7dcb54a/internal/cron/activity_cron.go#L81
- https://github.com/pterodactyl/wings/blob/9ffbcdcdb1163da823cf9959b9602df9f7dcb54a/internal/cron/sftp_cron.go#L86
