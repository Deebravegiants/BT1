# [H] CVE-2018-12551

## Summary
Severity: High
Advisory: CVE-2018-12551
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2018-12551
Type: osv

## Details
When Eclipse Mosquitto version 1.0 to 1.5.5 (inclusive) is configured to use a password file for authentication, any malformed data in the password file will be treated as valid. This typically means that the malformed data becomes a username and no password. If this occurs, clients can circumvent authentication and get access to the broker by using the malformed username. In particular, a blank line will be treated as a valid empty username. Other security measures are unaffected. Users who have only used the mosquitto_passwd utility to create and modify their password files are unaffected by this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2019/10/msg00035.html
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=543401
