# [H] CVE-2021-36370

## Summary
Severity: High
Advisory: CVE-2021-36370
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-36370
Type: osv

## Details
An issue was discovered in Midnight Commander through 4.8.26. When establishing an SFTP connection, the fingerprint of the server is neither checked nor displayed. As a result, a user connects to the server without the ability to verify its authenticity.

## References
- https://mail.gnome.org/archives/mc-devel/2021-August/msg00008.html
- https://midnight-commander.org/
- https://sourceforge.net/projects/mcwin32/files/
- https://docs.ssh-mitm.at/CVE-2021-36370.html
- https://github.com/MidnightCommander/mc/blob/5c1d3c55dd15356ec7d079084d904b7b0fd58d3e/src/vfs/sftpfs/connection.c#L484
- https://github.com/MidnightCommander/mc/blob/master/src/vfs/sftpfs/connection.c
