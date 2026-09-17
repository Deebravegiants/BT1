# [C] CVE-2021-28119

## Summary
Severity: Critical
Advisory: CVE-2021-28119
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-28119
Type: osv

## Details
Twinkle Tray (aka twinkle-tray) through 1.13.3 allows remote command execution. A remote attacker may send a crafted IPC message to the exposed vulnerable ipcRenderer IPC interface, which invokes the dangerous openExternal API.

## References
- https://github.com/xanderfrangos/twinkle-tray/issues/142
