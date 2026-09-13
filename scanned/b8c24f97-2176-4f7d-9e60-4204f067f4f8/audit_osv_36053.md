# [H] CVE-2026-19401

## Summary
Severity: High
Advisory: CVE-2026-19401
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-19401
Type: osv

## Details
Any remote client can crash a (debugging/non-release build type) NSD serve child by sending it a special crafted message with a specially tuned number of DNS Cookie options (17 when UDP payload size is 512). By continuously crashing the serve childs, the remote client can severely hamper or, when positioned sufficiently close, deny all DNS service.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-19401.txt
