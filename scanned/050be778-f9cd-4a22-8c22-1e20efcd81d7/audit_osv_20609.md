# [H] CVE-2021-35523

## Summary
Severity: High
Advisory: CVE-2021-35523
Aliases: GHSA-v8p8-4w8f-qh34
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-35523
Type: osv

## Details
Securepoint SSL VPN Client v2 before 2.0.32 on Windows has unsafe configuration handling that enables local privilege escalation to NT AUTHORITY\SYSTEM. A non-privileged local user can modify the OpenVPN configuration stored under "%APPDATA%\Securepoint SSL VPN" and add a external script file that is executed as privileged user.

## References
- http://seclists.org/fulldisclosure/2021/Jun/59
- https://github.com/Securepoint/openvpn-client/security/advisories/GHSA-v8p8-4w8f-qh34
- http://packetstormsecurity.com/files/163320/Securepoint-SSL-VPN-Client-2.0.30-Local-Privilege-Escalation.html
- https://bogner.sh/2021/04/local-privilege-escalation-in-securepoint-ssl-vpn-client-2-0-30/
