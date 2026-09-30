# [H] CVE-2021-33356

## Summary
Severity: High
Advisory: CVE-2021-33356
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-09
Source: https://osv.dev/vulnerability/CVE-2021-33356
Type: osv

## Details
Multiple privilege escalation vulnerabilities in RaspAP 1.5 to 2.6.5 could allow an authenticated remote attacker to inject arbitrary commands to /installers/common.sh component that can result in remote command execution with root privileges.

## References
- https://gist.github.com/omriinbar/52c000c02a6992c6ce68d531195f69cf
- https://github.com/RaspAP/raspap-webgui/blob/5a7b77459839c9420fac0d10ec28cee1af9bb782/installers/common.sh#L216
- https://github.com/RaspAP/raspap-webgui/blob/5a7b77459839c9420fac0d10ec28cee1af9bb782/installers/common.sh#L231
- https://github.com/RaspAP/raspap-webgui/blob/5a7b77459839c9420fac0d10ec28cee1af9bb782/installers/common.sh#L314
- https://github.com/RaspAP/raspap-webgui/blob/5a7b77459839c9420fac0d10ec28cee1af9bb782/installers/common.sh#L407
- https://github.com/RaspAP/raspap-webgui/blob/5a7b77459839c9420fac0d10ec28cee1af9bb782/installers/common.sh#L510
