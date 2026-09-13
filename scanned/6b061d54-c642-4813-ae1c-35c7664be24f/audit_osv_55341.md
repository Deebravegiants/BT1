# [H] CVE-2025-32801

## Summary
Severity: High
Advisory: CVE-2025-32801
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-28
Source: https://osv.dev/vulnerability/CVE-2025-32801
Type: osv

## Details
Kea configuration and API directives can be used to load a malicious hook library.  Many common configurations run Kea as root, leave the API entry points unsecured by default, and/or place the control sockets in insecure paths.
This issue affects Kea versions 2.4.0 through 2.4.1, 2.6.0 through 2.6.2, and 2.7.0 through 2.7.8.

## References
- https://kb.isc.org/docs/cve-2025-32801
