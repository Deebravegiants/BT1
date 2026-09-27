# [C] CVE-2018-7544

## Summary
Severity: Critical
Advisory: CVE-2018-7544
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-03-16
Source: https://osv.dev/vulnerability/CVE-2018-7544
Type: osv

## Details
A cross-protocol scripting issue was discovered in the management interface in OpenVPN through 2.4.5. When this interface is enabled over TCP without a password, and when no other clients are connected to this interface, attackers can execute arbitrary management commands, obtain sensitive information, or cause a denial of service (SIGTERM) by triggering XMLHttpRequest actions in a web browser. This is demonstrated by a multipart/form-data POST to http://localhost:23000 with a "signal SIGTERM" command in a TEXTAREA element. NOTE: The vendor disputes that this is a vulnerability. They state that this is the result of improper configuration of the OpenVPN instance rather than an intrinsic vulnerability, and now more explicitly warn against such configurations in both the management-interface documentation, and with a runtime warning

## References
- http://blog.0xlabs.com/2018/03/openvpn-remote-information-disclosure.html
