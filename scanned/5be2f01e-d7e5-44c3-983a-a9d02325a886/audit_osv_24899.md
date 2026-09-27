# [H] CVE-2023-2829

## Summary
Severity: High
Advisory: CVE-2023-2829
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-21
Source: https://osv.dev/vulnerability/CVE-2023-2829
Type: osv

## Details
A `named` instance configured to run as a DNSSEC-validating recursive resolver with the Aggressive Use of DNSSEC-Validated Cache (RFC 8198) option (`synth-from-dnssec`) enabled can be remotely terminated using a zone with a malformed NSEC record.
This issue affects BIND 9 versions 9.16.8-S1 through 9.16.41-S1 and 9.18.11-S1 through 9.18.15-S1.

## References
- https://kb.isc.org/docs/cve-2023-2829
- https://security.netapp.com/advisory/ntap-20230703-0010/
