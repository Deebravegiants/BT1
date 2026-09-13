# [M] CVE-2016-8750

## Summary
Severity: Medium
Advisory: CVE-2016-8750
Aliases: GHSA-chj8-5xgw-wcvj
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2016-8750
Type: osv

## Details
Apache Karaf prior to 4.0.8 used the LDAPLoginModule to authenticate users to a directory via LDAP. However, it did not encoding usernames properly and hence was vulnerable to LDAP injection attacks leading to a denial of service.

## References
- http://www.securityfocus.com/bid/103098
- https://access.redhat.com/errata/RHSA-2018:1322
- https://karaf.apache.org/security/cve-2016-8750.txt
