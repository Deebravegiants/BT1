# [H] CVE-2017-14102

## Summary
Severity: High
Advisory: CVE-2017-14102
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-09-01
Source: https://osv.dev/vulnerability/CVE-2017-14102
Type: osv

## Details
MIMEDefang 2.80 and earlier creates a PID file after dropping privileges to a non-root account, which might allow local users to kill arbitrary processes by leveraging access to this non-root account for PID file modification before a root script executes a "kill `cat /pathname`" command, as demonstrated by the init-script.in and mimedefang-init.in scripts.

## References
- http://lists.roaringpenguin.com/pipermail/mimedefang/2017-August/038077.html
- http://lists.roaringpenguin.com/pipermail/mimedefang/2017-August/038085.html
