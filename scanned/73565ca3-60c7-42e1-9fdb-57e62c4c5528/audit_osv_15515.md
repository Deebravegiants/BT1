# [H] CVE-2019-16964

## Summary
Severity: High
Advisory: CVE-2019-16964
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-16964
Type: osv

## Details
app/call_centers/cmd.php in the Call Center Queue Module in FusionPBX up to 4.5.7 suffers from a command injection vulnerability due to a lack of input validation, which allows authenticated attackers (with at least the permission call_center_queue_add or call_center_queue_edit) to execute any commands on the host as www-data.

## References
- https://resp3ctblog.wordpress.com/2019/10/19/fusionpbx-sofia-api-command-injection-1/
- https://github.com/fusionpbx/fusionpbx/commit/2f9e591a4034c3aea70185dcab837946096449bf
