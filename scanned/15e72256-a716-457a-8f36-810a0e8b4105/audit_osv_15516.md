# [H] CVE-2019-16965

## Summary
Severity: High
Advisory: CVE-2019-16965
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16965
Type: osv

## Details
resources/cmd.php in FusionPBX up to 4.5.7 suffers from a command injection vulnerability due to a lack of input validation, which allows authenticated administrative attackers to execute any commands on the host as www-data.

## References
- https://github.com/fusionpbx/fusionpbx/commit/6baad9af1bc55c80b793af3bd1ac35b39c20b173
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-sofia-api-command-injection-2/
