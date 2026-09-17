# [H] CVE-2021-3606

## Summary
Severity: High
Advisory: CVE-2021-3606
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-02
Source: https://osv.dev/vulnerability/CVE-2021-3606
Type: osv

## Details
OpenVPN before version 2.5.3 on Windows allows local users to load arbitrary dynamic loadable libraries via an OpenSSL configuration file if present, which allows the user to run arbitrary code with the same privilege level as the main OpenVPN process (openvpn.exe).

## References
- https://community.openvpn.net/openvpn/wiki/CVE-2021-3606
- https://community.openvpn.net/openvpn/wiki/SecurityAnnouncements
