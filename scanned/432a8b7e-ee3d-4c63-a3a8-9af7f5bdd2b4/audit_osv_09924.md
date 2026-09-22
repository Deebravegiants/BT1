# [H] CVE-2017-12173

## Summary
Severity: High
Advisory: CVE-2017-12173
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-12173
Type: osv

## Details
It was found that sssd's sysdb_search_user_by_upn_res() function before 1.16.0 did not sanitize requests when querying its local cache and was vulnerable to injection. In a centralized login environment, if a password hash was locally cached for a given user, an authenticated attacker could use this flaw to retrieve it.

## References
- https://access.redhat.com/errata/RHSA-2017:3379
- https://access.redhat.com/errata/RHSA-2018:1877
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12173
