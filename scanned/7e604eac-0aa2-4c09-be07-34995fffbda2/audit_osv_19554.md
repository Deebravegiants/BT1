# [H] CVE-2021-22001

## Summary
Severity: High
Advisory: CVE-2021-22001
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-07-22
Source: https://osv.dev/vulnerability/CVE-2021-22001
Type: osv

## Details
In UAA versions prior to 75.3.0, sensitive information like relaying secret of the provider was revealed in response when deletion request of an identity provider( IdP) of type “oauth 1.0” was sent to UAA server.

## References
- https://www.cloudfoundry.org/blog/cve-2021-22001-sensitive-info-leakage-in-uaa-during-identity-provider-deletion/
