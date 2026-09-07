# [H] phpMyFAQ Generates an Error Message Containing Sensitive Information if database server is not available

## Summary
Severity: High
Advisory: GHSA-vrjr-p3xp-xx2x
CVE: CVE-2024-54141
CWE: CWE-209
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-12-06
Source: https://github.com/advisories/GHSA-vrjr-p3xp-xx2x
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.0.0

## Details
### Summary
Exposure of database (ie postgreSQL) server's credential when connection to DB fails.

### Details
Exposed database credentials upon misconfig/DoS @ permalink: https://github.com/thorsten/phpMyFAQ/blob/main/phpmyfaq/src/phpMyFAQ/Setup/Installer.php#L694

### PoC
When postgreSQL server is unreachable, an error would be thrown exposing the credentials of the database. For instance, when "http://<phpmyfaq-instance>:8080/setup/index.php" is hit when the database instance/server is down, then credentials are exposed, for instance:

```
( ! ) Warning: pg_connect(): Unable to connect to PostgreSQL server: connection to server at &quot;127.0.0.1&quot;, port 5432 failed: Connection refused Is the server running on that host and accepting TCP/IP connections? in /var/www/html/src/phpMyFAQ/Database/Pgsql.php on line 78
Call Stack
# Time Memory Function Location
1 0.0404 453880 {main}( ) .../index.php:0
2 1.1341 610016 phpMyFAQ\Setup\Installer->startInstall( $setup = ??? ) .../index.php:471
3 1.2113 611544 phpMyFAQ\Database\Pgsql->connect( $host = '127.0.0.1', $user = 'cvecve', $password = '<redacted>', $database = 'cvecve', $port = 5432 ) .../Installer.php:694
4 1.2113 611864 pg_connect( $connection_string = 'host=127.0.0.1 port=5432 dbname=cvecve user=cvecve password=<redacted>' ) .../Pgsql.php:78

( ! ) Fatal error: Uncaught TypeError: Cannot assign false to property phpMyFAQ\Database\Pgsql::$conn of type ?PgSql\Connection in /var/www/html/src/phpMyFAQ/Database/Pgsql.php on line 78
( ! ) TypeError: Cannot assign false to property phpMyFAQ\Database\Pgsql::$conn of type ?PgSql\Connection in /var/www/html/src/phpMyFAQ/Database/Pgsql.php on line 78
Call Stack
# Time Memory Function Location
1 0.0404 453880 {main}( ) .../index.php:0
2 1.1341 610016 phpMyFAQ\Setup\Installer->startInstall( $setup = ??? ) .../index.php:471
3 1.2113 611544 phpMyFAQ\Database\Pgsql->connect( $host = '127.0.0.1', $user = 'cvecve', $password = '<redacted>', $database = 'cvecve', $port = 5432 ) .../Installer.php:694
```
![image](https://github.com/user-attachments/assets/feb9c0ba-0cf7-44d1-bd86-87cc36292b70)

A way to force this would be to perform a denial of service on the database instance/server. When the db connection is refused, the credentials would show. The remote attacker can then use that to gain full control on the database.

### Impact
This vulnerability exposes the credentials of the database and grants a remote attacker full control over the database.

First notified Snyk on 16 Jan 2024.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-vrjr-p3xp-xx2x
- https://nvd.nist.gov/vuln/detail/CVE-2024-54141
- https://github.com/thorsten/phpMyFAQ/commit/b9289a0b2233df864361c131cd177b6715fbb0fe
- https://github.com/thorsten/phpMyFAQ
