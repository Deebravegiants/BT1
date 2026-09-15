# [H] CVE-2024-28872

## Summary
Severity: High
Advisory: CVE-2024-28872
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-11
Source: https://osv.dev/vulnerability/CVE-2024-28872
Type: osv

## Details
The TLS certificate validation code is flawed. An attacker can obtain a TLS certificate from the Stork server and use it to connect to the Stork agent. Once this connection is established with the valid certificate, the attacker can send malicious commands to a monitored service (Kea or BIND 9), possibly resulting in confidential data loss and/or denial of service. It should be noted that this vulnerability is not related to BIND 9 or Kea directly, and only customers using the Stork management tool are potentially affected.
This issue affects Stork versions 0.15.0 through 1.15.0.

## References
- https://kb.isc.org/docs/cve-2024-28872
