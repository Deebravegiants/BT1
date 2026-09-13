# [H] BIT-openldap-2020-25692

## Summary
Severity: High
Advisory: BIT-openldap-2020-25692
Aliases: CVE-2020-25692
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-openldap-2020-25692
Type: osv

## Affected
- Bitnami: `openldap` — affected >=0 <2.4.55

## Details
A NULL pointer dereference was found in OpenLDAP server and was fixed in openldap 2.4.55, during a request for renaming RDNs. An unauthenticated attacker could remotely crash the slapd process by sending a specially crafted request, causing a Denial of Service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1894567
- https://security.netapp.com/advisory/ntap-20210108-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2020-25692
