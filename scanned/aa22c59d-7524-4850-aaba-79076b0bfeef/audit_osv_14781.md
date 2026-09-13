# [H] CVE-2019-11410

## Summary
Severity: High
Advisory: CVE-2019-11410
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-17
Source: https://osv.dev/vulnerability/CVE-2019-11410
Type: osv

## Details
app/backup/index.php in the Backup Module in FusionPBX 4.4.3 suffers from a command injection vulnerability due to a lack of input validation, which allows authenticated administrative attackers to execute commands on the host.

## References
- https://blog.gdssecurity.com/labs/2019/6/7/rce-using-caller-id-multiple-vulnerabilities-in-fusionpbx.html
- https://github.com/fusionpbx/fusionpbx/commit/0f965c89288de449236ad6de4f97960814ce8c84
