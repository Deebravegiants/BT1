# [H] Potential Backup file leaked via Nginx in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-53991
Aliases: CVE-2024-53991, GHSA-567m-82f6-56rv
Ecosystem: Bitnami
Published: 2024-12-23
Source: https://osv.dev/vulnerability/BIT-discourse-2024-53991
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.3.3

## Details
Discourse is an open source platform for community discussion. This vulnerability only impacts Discourse instances configured to use `FileStore::LocalStore` which means uploads and backups are stored locally on disk. If an attacker knows the name of the Discourse backup file, the attacker can trick nginx into sending the Discourse backup file with a well crafted request. This issue is patched in the latest stable, beta and tests-passed versions of Discourse. Users are advised to upgrade. Users unable to upgrade can either 1. Download all local backups on to another storage device, disable the `enable_backups` site setting and delete all backups until the site has been upgraded to pull in the fix. Or  2. Change the `backup_location` site setting to `s3` so that backups are stored and downloaded directly from S3.

## References
- https://github.com/discourse/discourse/security/advisories/GHSA-567m-82f6-56rv
- https://nvd.nist.gov/vuln/detail/CVE-2024-53991
