# [H] BIT-mariadb-2020-7221

## Summary
Severity: High
Advisory: BIT-mariadb-2020-7221
Aliases: BIT-mariadb-min-2020-7221, BIT-mysql-client-2020-7221, CVE-2020-7221
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2020-7221
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.4.7 <10.4.12

## Details
mysql_install_db in MariaDB 10.4.7 through 10.4.11 allows privilege escalation from the mysql user account to root because chown and chmod are performed unsafely, as demonstrated by a symlink attack on a chmod 04755 of auth_pam_tool_dir/auth_pam_tool. NOTE: this does not affect the Oracle MySQL product, which implements mysql_install_db differently.

## References
- https://bugzilla.suse.com/show_bug.cgi?id=1160868
- https://github.com/MariaDB/server/commit/9d18b6246755472c8324bf3e20e234e08ac45618
- https://seclists.org/oss-sec/2020/q1/55
- https://nvd.nist.gov/vuln/detail/CVE-2020-7221
