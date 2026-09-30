# [H] openssl on Windows built with openssldir set from the build machine (Uncontrolled Search Path Element)

## Summary
Severity: High
Advisory: CVE-2026-34054
Aliases: GHSA-p322-v6vw-vrq9
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34054
Type: osv

## Details
vcpkg is a free and open-source C/C++ package manager. Prior to version 3.6.1#3, vcpkg's Windows builds of OpenSSL set openssldir to a path on the build machine, making that path be attackable later on customer machines. This issue has been patched in version 3.6.1#3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34054.json
- https://github.com/microsoft/vcpkg/security/advisories/GHSA-p322-v6vw-vrq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-34054
- https://github.com/microsoft/vcpkg/commit/5111afdf55cc1429d9951e4c7b02010e659346a9
- https://github.com/microsoft/vcpkg/pull/50518
