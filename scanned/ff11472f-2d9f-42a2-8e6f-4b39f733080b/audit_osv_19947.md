# [C] CVE-2021-28154

## Summary
Severity: Critical
Advisory: CVE-2021-28154
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-28154
Type: osv

## Details
Camunda Modeler (aka camunda-modeler) through 4.6.0 allows arbitrary file access. A remote attacker may send a crafted IPC message to the exposed vulnerable ipcRenderer IPC interface, which manipulates the readFile and writeFile APIs. NOTE: the vendor states "The way we secured the app is that it does not allow any remote scripts to be opened, no unsafe scripts to be evaluated, no remote sites to be browsed.

## References
- https://github.com/camunda/camunda-modeler/issues/2143
