# [H] CVE-2026-18916

## Summary
Severity: High
Advisory: CVE-2026-18916
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-18916
Type: osv

## Details
Any remote client can crash a NSD serve child, by throttling the TCP receive window after a TCP query. By continuously crashing the serve childs, the remote client can denial all TCP service to this NSD instance.

## References
- https://www.nlnetlabs.nl/downloads/nsd/CVE-2026-18916.txt
