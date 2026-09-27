# [H] CVE-2022-3276

## Summary
Severity: High
Advisory: CVE-2022-3276
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-07
Source: https://osv.dev/vulnerability/CVE-2022-3276
Type: osv

## Details
Command injection is possible in the puppetlabs-mysql module prior to version 13.0.0. A malicious actor is able to exploit this vulnerability only if they are able to provide unsanitized input to the module. This condition is rare in most deployments of Puppet and Puppet Enterprise.

## References
- https://puppet.com/security/cve/CVE-2022-3276
