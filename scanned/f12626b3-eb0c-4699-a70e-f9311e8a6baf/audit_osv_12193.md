# [H] CVE-2018-1086

## Summary
Severity: High
Advisory: CVE-2018-1086
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-12
Source: https://osv.dev/vulnerability/CVE-2018-1086
Type: osv

## Details
pcs before versions 0.9.164 and 0.10 is vulnerable to a debug parameter removal bypass. REST interface of the pcsd service did not properly remove the pcs debug argument from the /run_pcs query, possibly disclosing sensitive information. A remote attacker with a valid token could use this flaw to elevate their privilege.

## References
- https://access.redhat.com/errata/RHSA-2018:1060
- https://access.redhat.com/errata/RHSA-2018:1927
- https://www.debian.org/security/2018/dsa-4169
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1086
