# [C] CVE-2021-41392

## Summary
Severity: Critical
Advisory: CVE-2021-41392
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-09-17
Source: https://osv.dev/vulnerability/CVE-2021-41392
Type: osv

## Details
static/main-preload.js in Boost Note through 0.22.0 allows remote command execution. A remote attacker may send a crafted IPC message to the exposed vulnerable ipcRenderer IPC interface, which invokes the dangerous openExternal Electron API.

## References
- https://github.com/BoostIO/BoostNote-App/issues/856
