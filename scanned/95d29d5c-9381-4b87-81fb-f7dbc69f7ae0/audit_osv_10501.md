# [H] CVE-2017-16641

## Summary
Severity: High
Advisory: CVE-2017-16641
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-07
Source: https://osv.dev/vulnerability/CVE-2017-16641
Type: osv

## Details
lib/rrd.php in Cacti 1.1.27 allows remote authenticated administrators to execute arbitrary OS commands via the path_rrdtool parameter in an action=save request to settings.php.

## References
- https://github.com/Cacti/cacti/issues/1057
