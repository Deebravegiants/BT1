# [H] CVE-2025-70083

## Summary
Severity: High
Advisory: CVE-2025-70083
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2025-70083
Type: osv

## Details
An issue was discovered in OpenSatKit 2.2.1. The DirName field in the telecommand is provided by the ground segment and must be treated as untrusted input. The program copies DirName into the local buffer DirWithSep using strcpy. The size of this buffer is OS_MAX_PATH_LEN. If the length of DirName is greater than or equal to OS_MAX_PATH_LEN, a stack buffer overflow occurs, overwriting adjacent stack memory. The path length check (FileUtil_AppendPathSep) is performed after the strcpy operation, meaning the validation occurs too late and cannot prevent the overflow.

## References
- https://gist.github.com/jonafk555
- https://github.com/OpenSatKit/OpenSatKit/releases/tag/v2.2.1
- https://raw.githubusercontent.com/OpenSatKit/OpenSatKit/master/cfs/apps/filemgr/fsw/src/dir.c
- https://raw.githubusercontent.com/OpenSatKit/OpenSatKit/master/cfs/apps/filemgr/fsw/src/dir.c#:~:text=strcpy%28DirWithSep
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70083.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70083
- https://github.com/OpenSatKit/OpenSatKit
