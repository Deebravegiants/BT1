# [H] CVE-2018-12543

## Summary
Severity: High
Advisory: CVE-2018-12543
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-15
Source: https://osv.dev/vulnerability/CVE-2018-12543
Type: osv

## Details
In Eclipse Mosquitto versions 1.5 to 1.5.2 inclusive, if a message is published to Mosquitto that has a topic starting with $, but that is not $SYS, e.g. $test/test, then an assert is triggered that should otherwise not be reachable and Mosquitto will exit.

## References
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=539295
