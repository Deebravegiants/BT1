# [C] CVE-2021-28134

## Summary
Severity: Critical
Advisory: CVE-2021-28134
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-11
Source: https://osv.dev/vulnerability/CVE-2021-28134
Type: osv

## Details
Clipper before 1.0.5 allows remote command execution. A remote attacker may send a crafted IPC message to the exposed vulnerable ipcRenderer IPC interface, which invokes the dangerous openExternal API.

## References
- https://github.com/AkashRajpurohit/clipper/pull/14
- https://github.com/AkashRajpurohit/clipper/pull/14/commits/28f1492a12234cf1e6af85c78bf22ee2f5090d19
- https://github.com/AkashRajpurohit/clipper/releases/tag/v1.0.5
- https://github.com/AkashRajpurohit/clipper/issues/13
