# [M] CVE-2021-28941

## Summary
Severity: Medium
Advisory: CVE-2021-28941
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/CVE-2021-28941
Type: osv

## Details
Because of no validation on a curl command in MagpieRSS 0.72 in the /extlib/Snoopy.class.inc file, when you send a request to the /scripts/magpie_debug.php or /scripts/magpie_simple.php page, it's possible to request any internal page if you use a https request.

## References
- https://github.com/kellan/magpierss/blob/04d2a88b97fdba5813d01dc0d56c772d97360bb5/extlib/Snoopy.class.inc#L660
- https://pastebin.com/kpzHKKJu
