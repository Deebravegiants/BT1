# [H] CVE-2024-47850

## Summary
Severity: High
Advisory: CVE-2024-47850
Aliases: GHSA-rq86-c7g6-r2h8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-04
Source: https://osv.dev/vulnerability/CVE-2024-47850
Type: osv

## Details
CUPS cups-browsed before 2.5b1 will send an HTTP POST request to an arbitrary destination and port in response to a single IPP UDP packet requesting a printer to be added, a different vulnerability than CVE-2024-47176. (The request is meant to probe the new printer but can be used to create DDoS amplification attacks.)

## References
- http://www.openwall.com/lists/oss-security/2024/10/04/1
- https://security.netapp.com/advisory/ntap-20241011-0002/
- https://github.com/OpenPrinting/cups-filters/security/advisories/GHSA-rq86-c7g6-r2h8
- https://github.com/OpenPrinting/cups
- https://www.akamai.com/blog/security-research/october-cups-ddos-threat
