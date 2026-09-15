# [C] CVE-2020-24383

## Summary
Severity: Critical
Advisory: CVE-2020-24383
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2020-12-11
Source: https://osv.dev/vulnerability/CVE-2020-24383
Type: osv

## Details
An issue was discovered in FNET through 4.6.4. The code for processing resource records in mDNS queries doesn't check for proper '\0' termination of the resource record name string, leading to an out-of-bounds read, and potentially causing information leak or Denial-or-Service.

## References
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-01
- https://www.kb.cert.org/vuls/id/815128
