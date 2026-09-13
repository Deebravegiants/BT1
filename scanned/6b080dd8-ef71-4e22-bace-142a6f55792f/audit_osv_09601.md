# [C] CVE-2017-1000362

## Summary
Severity: Critical
Advisory: CVE-2017-1000362
Aliases: GHSA-92mr-4w2q-4578
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-1000362
Type: osv

## Details
The re-key admin monitor was introduced in Jenkins 1.498 and re-encrypted all secrets in JENKINS_HOME with a new key. It also created a backup directory with all old secrets, and the key used to encrypt them. These backups were world-readable and not removed afterwards. Jenkins now deletes the backup directory, if present. Upgrading from before 1.498 will no longer create a backup directory. Administrators relying on file access permissions in their manually created backups are advised to check them for the directory $JENKINS_HOME/jenkins.security.RekeySecretAdminMonitor/backups, and delete it if present.

## References
- https://jenkins.io/security/advisory/2017-02-01/
