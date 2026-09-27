# [H] CVE-2017-2591

## Summary
Severity: High
Advisory: CVE-2017-2591
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2017-2591
Type: osv

## Details
389-ds-base before version 1.3.6 is vulnerable to an improperly NULL terminated array in the uniqueness_entry_to_config() function in the "attribute uniqueness" plugin of 389 Directory Server. An authenticated, or possibly unauthenticated, attacker could use this flaw to force an out-of-bound heap memory read, possibly triggering a crash of the LDAP service.

## References
- http://www.securityfocus.com/bid/95670
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2591
- https://pagure.io/389-ds-base/issue/48986
