# [H] CVE-2021-41531

## Summary
Severity: High
Advisory: CVE-2021-41531
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-09-21
Source: https://osv.dev/vulnerability/CVE-2021-41531
Type: osv

## Details
NLnet Labs Routinator prior to 0.10.0 produces invalid RTR payload if an RPKI CA uses too large values in the max-length parameter in a ROA. This will lead to RTR clients such as routers to reject the RPKI data set, effectively disabling Route Origin Validation.

## References
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2021-41531.txt
