# [M] CVE-2021-3515

## Summary
Severity: Medium
Advisory: CVE-2021-3515
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-3515
Type: osv

## Details
A shell injection flaw was found in pglogical in versions before 2.3.4 and before 3.6.26. An attacker with CREATEDB privileges on a PostgreSQL server can craft a database name that allows execution of shell commands as the postgresql user when calling pglogical.create_subscription().

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1954112
