# [M] CVE-2023-46871

## Summary
Severity: Medium
Advisory: CVE-2023-46871
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-12-07
Source: https://osv.dev/vulnerability/CVE-2023-46871
Type: osv

## Details
GPAC version 2.3-DEV-rev602-ged8424300-master in MP4Box contains a memory leak in NewSFDouble scenegraph/vrml_tools.c:300. This vulnerability may lead to a denial of service.

## References
- https://github.com/gpac/gpac/issues/2658
- https://gist.github.com/ReturnHere/d0899bb03b8f5e8fae118f2b76888486
