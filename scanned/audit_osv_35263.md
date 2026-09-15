# [C] CVE-2025-70085

## Summary
Severity: Critical
Advisory: CVE-2025-70085
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2025-70085
Type: osv

## Details
An issue was discovered in OpenSatKit 2.2.1. The EventErrStr buffer has a fixed size of 256 bytes. The code uses sprintf to format two filenames (Source1Filename and the string returned by FileUtil_FileStateStr) into this buffer without any length checking and without using bounded format specifiers such as %.*s. If the filename length approaches OS_MAX_PATH_LEN (commonly 64-256 bytes), the combined formatted string together with constant text can exceed 256 bytes, resulting in a stack buffer overflow. Such unsafe sprintf calls are scattered across multiple functions in file.c, including FILE_ConcatenateCmd() and ConcatenateFiles(), all of which fail to validate the output length.

## References
- https://gist.github.com/jonafk555
- https://github.com/OpenSatKit/OpenSatKit/releases/tag/v2.2.1
- https://raw.githubusercontent.com/OpenSatKit/OpenSatKit/master/cfs/apps/filemgr/fsw/src/file.c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70085.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70085
- https://github.com/OpenSatKit/OpenSatKit
