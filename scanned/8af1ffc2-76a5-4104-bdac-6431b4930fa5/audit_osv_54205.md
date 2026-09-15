# [H] CVE-2023-43115

## Summary
Severity: High
Advisory: CVE-2023-43115
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-09-18
Source: https://osv.dev/vulnerability/CVE-2023-43115
Type: osv

## Details
In Artifex Ghostscript through 10.01.2, gdevijs.c in GhostPDL can lead to remote code execution via crafted PostScript documents because they can switch to the IJS device, or change the IjsServer parameter, after SAFER has been activated. NOTE: it is a documented risk that the IJS server can be specified on a gs command line (the IJS device inherently must execute a command to start the IJS server).

## References
- https://ghostscript.com/
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=e59216049cac290fb437a04c4f41ea46826cfba5
- https://bugs.ghostscript.com/show_bug.cgi?id=707051
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IK3UXJ5HKMPAL5EQELJAWSRPA2AUOJJO/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PG5AQV7JOL5TAU76FWPJCMSKO5DREKV5/
