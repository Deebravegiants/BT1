# [H] CVE-2018-14638

## Summary
Severity: High
Advisory: CVE-2018-14638
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-14
Source: https://osv.dev/vulnerability/CVE-2018-14638
Type: osv

## Details
A flaw was found in 389-ds-base before version 1.3.8.4-13. The process ns-slapd crashes in delete_passwdPolicy function when persistent search connections are terminated unexpectedly leading to remote denial of service.

## References
- https://access.redhat.com/errata/RHSA-2018:2757
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14638
- https://pagure.io/389-ds-base/c/78fc627accacfa4061ce48977e22301f81ea8d73
