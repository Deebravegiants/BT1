# [M] CVE-2023-24626

## Summary
Severity: Medium
Advisory: CVE-2023-24626
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-04-08
Source: https://osv.dev/vulnerability/CVE-2023-24626
Type: osv

## Details
socket.c in GNU Screen through 4.9.0, when installed setuid or setgid (the default on platforms such as Arch Linux and FreeBSD), allows local users to send a privileged SIGHUP signal to any PID, causing a denial of service or disruption of the target process.

## References
- https://www.exploit-db.com/exploits/51252
- https://security.netapp.com/advisory/ntap-20250509-0003/
- https://savannah.gnu.org/bugs/?63195
- https://git.savannah.gnu.org/cgit/screen.git/patch/?id=e9ad41bfedb4537a6f0de20f00b27c7739f168f7
