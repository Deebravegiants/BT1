# [M] CVE-2021-3413

## Summary
Severity: Medium
Advisory: CVE-2021-3413
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2021-04-08
Source: https://osv.dev/vulnerability/CVE-2021-3413
Type: osv

## Details
A flaw was found in Red Hat Satellite in tfm-rubygem-foreman_azure_rm in versions before 2.2.0. A credential leak was identified which will expose Azure Resource Manager's secret key through JSON of the API output. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1930352
