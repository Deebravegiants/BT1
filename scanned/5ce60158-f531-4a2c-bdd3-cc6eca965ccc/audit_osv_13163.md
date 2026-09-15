# [C] CVE-2018-18249

## Summary
Severity: Critical
Advisory: CVE-2018-18249
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-18249
Type: osv

## Details
Icinga Web 2 before 2.6.2 allows injection of PHP ini-file directives via vectors involving environment variables as the channel to send information to the attacker, such as a name=${PATH}_${APACHE_RUN_DIR}_${APACHE_RUN_USER} parameter to /icingaweb2/navigation/add or /icingaweb2/dashboard/new-dashlet.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00031.html
- https://herolab.usd.de/wp-content/uploads/sites/4/2018/12/usd20180030.txt
