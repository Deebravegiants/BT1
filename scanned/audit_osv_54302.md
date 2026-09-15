# [C] CVE-2023-46932

## Summary
Severity: Critical
Advisory: CVE-2023-46932
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-09
Source: https://osv.dev/vulnerability/CVE-2023-46932
Type: osv

## Details
Heap Buffer Overflow vulnerability in GPAC version 2.3-DEV-rev617-g671976fcc-master, allows attackers to execute arbitrary code and cause a denial of service (DoS) via str2ulong class in src/media_tools/avilib.c in gpac/MP4Box.

## References
- https://github.com/gpac/gpac/issues/2669
