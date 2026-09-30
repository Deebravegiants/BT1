# [M] iccDEV: UB at TiffImg.h

## Summary
Severity: Medium
Advisory: CVE-2026-34546
Aliases: GHSA-fxgq-wf5v-25pq
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34546
Type: osv

## Details
iccDEV provides a set of libraries and tools for working with ICC color management profiles. Prior to version 2.3.1.6, a crafted TIFF input can trigger Undefined Behavior (UB) due to division by zero in the TIFF handling code paths used by iccTiffDump. This issue has been patched in version 2.3.1.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34546.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-fxgq-wf5v-25pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34546
- https://github.com/InternationalColorConsortium/iccDEV/issues/719
- https://github.com/InternationalColorConsortium/iccDEV/pull/723
