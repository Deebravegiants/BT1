# [C] CVE-2021-28940

## Summary
Severity: Critical
Advisory: CVE-2021-28940
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/CVE-2021-28940
Type: osv

## Details
Because of a incorrect escaped exec command in MagpieRSS in 0.72 in the /extlib/Snoopy.class.inc file, it is possible to add a extra command to the curl binary. This creates an issue on the /scripts/magpie_debug.php and /scripts/magpie_simple.php page that if you send a specific https url in the RSS URL field, you are able to execute arbitrary commands.

## References
- https://github.com/kellan/magpierss/blob/04d2a88b97fdba5813d01dc0d56c772d97360bb5/extlib/Snoopy.class.inc#L660
- https://pastebin.com/kpzHKKJu
- https://www.exploit-db.com/exploits/49643
