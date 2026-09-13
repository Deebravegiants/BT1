# [C] CVE-2022-3275

## Summary
Severity: Critical
Advisory: CVE-2022-3275
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-3275
Type: osv

## Details
Command injection is possible in the puppetlabs-apt module prior to version 9.0.0. A malicious actor is able to exploit this vulnerability only if they are able to provide unsanitized input to the module. This condition is rare in most deployments of Puppet and Puppet Enterprise.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CH4NUKZKPY4MFQHFBTONJK2AWES4DFDA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YR5LIOF5VKS4DC2NQWXTMPPXOYJC46XC/
- https://puppet.com/security/cve/CVE-2022-3275
