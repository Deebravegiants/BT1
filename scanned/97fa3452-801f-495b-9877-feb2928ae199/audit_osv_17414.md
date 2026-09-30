# [C] CVE-2020-15121

## Summary
Severity: Critical
Advisory: CVE-2020-15121
Aliases: GHSA-r552-vp94-9358
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2020-07-20
Source: https://osv.dev/vulnerability/CVE-2020-15121
Type: osv

## Details
In radare2 before version 4.5.0, malformed PDB file names in the PDB server path cause shell injection. To trigger the problem it's required to open the executable in radare2 and run idpd to trigger the download. The shell code will execute, and will create a file called pwned in the current directory.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MWC7KNBETYE5MK6VIUU26LUIISIFGSBZ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YE77P5RSE2T7JHEKMWF2ARTSJGMPXCFY/
- https://github.com/radareorg/radare2/issues/16945
- https://github.com/radareorg/radare2/pull/16966
- https://github.com/radareorg/radare2/security/advisories/GHSA-r552-vp94-9358
- https://github.com/radareorg/radare2/commit/04edfa82c1f3fa2bc3621ccdad2f93bdbf00e4f9
