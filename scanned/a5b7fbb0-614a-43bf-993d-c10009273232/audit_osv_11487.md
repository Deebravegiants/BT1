# [H] CVE-2017-8038

## Summary
Severity: High
Advisory: CVE-2017-8038
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-8038
Type: osv

## Details
In Cloud Foundry Foundation Credhub-release version 1.1.0, access control lists (ACLs) enforce whether an authenticated user can perform an operation on a credential. For installations using ACLs, the ACL was bypassed for the CredHub interpolate endpoint, allowing authenticated applications to view any credential within the CredHub installation.

## References
- https://www.cloudfoundry.org/cve-2017-8038/
