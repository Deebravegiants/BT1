# [M] CVE-2018-15869

## Summary
Severity: Medium
Advisory: CVE-2018-15869
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-08-25
Source: https://osv.dev/vulnerability/CVE-2018-15869
Type: osv

## Details
An Amazon Web Services (AWS) developer who does not specify the --owners flag when describing images via AWS CLI, and therefore not properly validating source software per AWS recommended security best practices, may unintentionally load an undesired and potentially malicious Amazon Machine Image (AMI) from the uncurated public community AMI catalog.

## References
- http://www.securityfocus.com/bid/105172
- https://github.com/hashicorp/packer/issues/6584
