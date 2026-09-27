# [M] CVE-2017-6807

## Summary
Severity: Medium
Advisory: CVE-2017-6807
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2017-03-13
Source: https://osv.dev/vulnerability/CVE-2017-6807
Type: osv

## Details
mod_auth_mellon before 0.13.1 is vulnerable to a Cross-Site Session Transfer attack, where a user with access to one web site running on a server can copy their session cookie to a different web site on the same server to get access to that site.

## References
- http://www.securityfocus.com/bid/96843
- https://sympa.uninett.no/lists/uninett.no/arc/modmellon/2017-03/msg00008.html
- https://github.com/UNINETT/mod_auth_mellon/releases/tag/v0.13.1
