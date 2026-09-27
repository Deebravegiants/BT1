# [M] strongSwan 4.5.0 < 6.0.5 EAP-TTLS AVP Parsing Integer Underflow

## Summary
Severity: Medium
Advisory: CVE-2026-25075
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/CVE-2026-25075
Type: osv

## Details
strongSwan versions 4.5.0 prior to 6.0.5 contain an integer underflow vulnerability in the EAP-TTLS AVP parser that allows unauthenticated remote attackers to cause a denial of service by sending crafted AVP data with invalid length fields during IKEv2 authentication. Attackers can exploit the failure to validate AVP length fields before subtraction to trigger excessive memory allocation or NULL pointer dereference, crashing the charon IKE daemon.

## References
- https://lists.debian.org/debian-lts-announce/2026/03/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25075.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25075
- https://www.strongswan.org/blog/2026/03/23/strongswan-6.0.5-released.html
- https://www.vulncheck.com/advisories/strongswan-eap-ttls-avp-parsing-integer-underflow
- https://github.com/strongswan/strongswan
- https://www.strongswan.org/blog/2026/03/23/strongswan-vulnerability-(cve-2026-25075).html
- https://y637f9qq2x.com/posts/cve-2026-25075/
