# [H] CVE-2025-25475

## Summary
Severity: High
Advisory: CVE-2025-25475
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-18
Source: https://osv.dev/vulnerability/CVE-2025-25475
Type: osv

## Details
A NULL pointer dereference in the component /libsrc/dcrleccd.cc of DCMTK v3.6.9+ DEV allows attackers to cause a Denial of Service (DoS) via a crafted DICOM file.

## References
- https://git.dcmtk.org/?p=dcmtk.git;a=commit;h=bffa3e9116abb7038b432443f16b1bd390e80245
- https://lists.debian.org/debian-lts-announce/2025/06/msg00025.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25475.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25475
- https://github.com/DCMTK/dcmtk/commit/bffa3e9116abb7038b432443f16b1bd390e80245
