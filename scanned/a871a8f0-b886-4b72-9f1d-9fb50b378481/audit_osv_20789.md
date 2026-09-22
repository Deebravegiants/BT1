# [H] CVE-2021-3698

## Summary
Severity: High
Advisory: CVE-2021-3698
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-10
Source: https://osv.dev/vulnerability/CVE-2021-3698
Type: osv

## Details
A flaw was found in Cockpit in versions prior to 260 in the way it handles the certificate verification performed by the System Security Services Daemon (SSSD). This flaw allows client certificates to authenticate successfully, regardless of the Certificate Revocation List (CRL) configuration or the certificate status. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1992149
