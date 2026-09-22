# [H] CVE-2020-15070

## Summary
Severity: High
Advisory: CVE-2020-15070
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-15070
Type: osv

## Details
Zulip Server 2.x before 2.1.7 allows eval injection if a privileged attacker were able to write directly to the postgres database, and chose to write a crafted custom profile field value.

## References
- https://blog.zulip.com/2020/06/26/zulip-server-2-1-7-security-release/
