# [H] CVE-2017-14610

## Summary
Severity: High
Advisory: CVE-2017-14610
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-20
Source: https://osv.dev/vulnerability/CVE-2017-14610
Type: osv

## Details
bareos-dir, bareos-fd, and bareos-sd in bareos-core in Bareos 16.2.6 and earlier create a PID file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for PID file modification before a root script executes a "kill `cat /pathname`" command.

## References
- https://bugs.bareos.org/view.php?id=847
