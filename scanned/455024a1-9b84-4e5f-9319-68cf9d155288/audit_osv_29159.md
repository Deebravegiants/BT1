# [M] HEIF Heap OOB Read in OpenImageIO

## Summary
Severity: Medium
Advisory: CVE-2024-40630
Aliases: GHSA-jjm9-9m4m-c8p2
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/CVE-2024-40630
Type: osv

## Details
OpenImageIO is a toolset for reading, writing, and manipulating image files of any image file format relevant to VFX / animation via a format-agnostic API with a feature set, scalability, and robustness needed for feature film production. In affected versions there is a bug in the heif input functionality of OpenImageIO. Specifically, in `HeifInput::seek_subimage()`.  In the worst case, this can lead to an information disclosure vulnerability, particularly for programs that directly use the `ImageInput` APIs. This bug has been addressed in commit `0a2dcb4c` which is included in the 2.5.13.1 release. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/AcademySoftwareFoundation/OpenImageIO/blob/7c486a1121a4bf71d50ff555fab2770294b748d7/src/heif.imageio/heifinput.cpp#L250
- https://github.com/AcademySoftwareFoundation/OpenImageIO/security/advisories/GHSA-jjm9-9m4m-c8p2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40630.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40630
- https://github.com/AcademySoftwareFoundation/OpenImageIO/commit/0a2dcb4cf2c3fd4825a146cd3ad929d9d8305ce3
