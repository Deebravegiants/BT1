# [H] CVE-2021-26788

## Summary
Severity: High
Advisory: CVE-2021-26788
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-08
Source: https://osv.dev/vulnerability/CVE-2021-26788
Type: osv

## Details
Oryx Embedded CycloneTCP 1.7.6 to 2.0.0, fixed in 2.0.2, is affected by incorrect input validation, which may cause a denial of service (DoS). To exploit the vulnerability, an attacker needs to have TCP connectivity to the target system. Receiving a maliciously crafted TCP packet from an unauthenticated endpoint is sufficient to trigger the bug.

## References
- https://github.com/Oryx-Embedded/CycloneTCP/commit/de5336016edbe1e90327d0ed1cba5c4e49114366?branch=de5336016edbe1e90327d0ed1cba5c4e49114366&diff=split
