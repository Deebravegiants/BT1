# [H] CVE-2020-24572

## Summary
Severity: High
Advisory: CVE-2020-24572
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/CVE-2020-24572
Type: osv

## Details
An issue was discovered in includes/webconsole.php in RaspAP 2.5. With authenticated access, an attacker can use a misconfigured (and virtually unrestricted) web console to attack the underlying OS (Raspberry Pi) running this software, and execute commands on the system (including ones for uploading of files and execution of code).

## References
- https://github.com/billz/raspap-webgui/releases
- https://github.com/lb0x
- https://github.com/billz/raspap-webgui/commit/dd5ab7bdc213381ee552001dd80c41ca47afab00
- https://deadb0x.io/lunchb0x/cve-2020-24572/
