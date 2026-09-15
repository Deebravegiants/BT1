# [H] CVE-2019-3567

## Summary
Severity: High
Advisory: CVE-2019-3567
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-3567
Type: osv

## Details
In some configurations an attacker can inject a new executable path into the extensions.load file for osquery and hard link a parent folder of a malicious binary to a folder with known 'safe' permissions. Under those circumstances osquery will load said malicious executable with SYSTEM permissions. The solution is to migrate installations to the 'Program Files' directory on Windows which restricts unprivileged write access. This issue affects osquery prior to v3.4.0.

## References
- https://www.facebook.com/security/advisories/cve-2019-3567
