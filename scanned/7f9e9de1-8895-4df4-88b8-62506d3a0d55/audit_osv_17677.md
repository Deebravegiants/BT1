# [C] CVE-2020-1897

## Summary
Severity: Critical
Advisory: CVE-2020-1897
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-18
Source: https://osv.dev/vulnerability/CVE-2020-1897
Type: osv

## Details
A use-after-free is possible due to an error in lifetime management in the request adaptor when a malicious client invokes request error handling in a specific sequence. This issue affects versions of proxygen prior to v2020.05.18.00.

## References
- https://www.facebook.com/security/advisories/cve-2020-1897
