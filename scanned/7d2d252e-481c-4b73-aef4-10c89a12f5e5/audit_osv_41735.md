# [C] sysPass FileBackupService Authenticated OS Command Injection via Backup Path

## Summary
Severity: Critical
Advisory: CVE-2026-63725
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-63725
Type: osv

## Details
sysPass's FileBackupService::doBackupFiles() in lib/SP/Services/Backup/FileBackupService.php around line 388 builds a tar shell command by string-concatenating the backup directory path $this->path directly into the command line ('tar czf ' . $backupFileApp . ' ' . BASE_PATH . ' --exclude \"' . $this->path . '\" 2>&1') and passes the result to PHP's exec() with no application of escapeshellarg() and no validation of the path against a safe character set. The $this->path value is read from the sysPass configuration, which is persisted in the database and writable through the admin settings API and the admin UI. An administrator (or an attacker who has obtained an admin API token or admin session) can therefore store a backup path containing shell metacharacters and trigger a backup operation to execute arbitrary OS commands as the web server process user (typically www-data or apache). Because sysPass is a password manager whose sole purpose is to hold credentials for other systems, code execution as the web-server user permits reading sysPass's master password and encryption key from memory or configuration files, decrypting every stored credential in the database, exporting the entire password vault, pivoting to internal systems using the disclosed credentials, and installing persistent backdoors on the password-manager host.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63725.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63725
- https://github.com/nuxsmin/sysPass
- https://gist.github.com/W40X/6747ba1b7da7bb69b0c0e162628df279
