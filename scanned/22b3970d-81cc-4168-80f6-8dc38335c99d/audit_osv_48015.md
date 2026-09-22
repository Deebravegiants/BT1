# [H] CVE-2017-16921

## Summary
Severity: High
Advisory: CVE-2017-16921
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-08
Source: https://osv.dev/vulnerability/CVE-2017-16921
Type: osv

## Details
In OTRS 6.0.x up to and including 6.0.1, OTRS 5.0.x up to and including 5.0.24, and OTRS 4.0.x up to and including 4.0.26, an attacker who is logged into OTRS as an agent can manipulate form parameters (related to PGP) and execute arbitrary shell commands with the permissions of the OTRS or web server user.

## References
- http://packetstormsecurity.com/files/162295/OTRS-6.0.1-Remote-Command-Execution.html
- https://www.debian.org/security/2017/dsa-4066
- https://lists.debian.org/debian-lts-announce/2017/12/msg00015.html
- https://www.otrs.com/security-advisory-2017-09-security-update-otrs-framework/
- https://www.exploit-db.com/exploits/43853/
