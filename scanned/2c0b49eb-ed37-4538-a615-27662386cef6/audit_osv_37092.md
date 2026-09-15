# [H] CVE-2026-28364

## Summary
Severity: High
Advisory: CVE-2026-28364
Aliases: GHSA-j26j-m5xr-g23c, GHSA-m34r-cgq7-jhfm, OSEC-2026-01, OSEC-2026-18
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28364
Type: osv

## Details
In OCaml before 4.14.3 and 5.x before 5.4.1, a buffer over-read in Marshal deserialization (runtime/intern.c) enables remote code execution through a multi-phase attack chain. The vulnerability stems from missing bounds validation in the readblock() function, which performs unbounded memcpy() operations using attacker-controlled lengths from crafted Marshal data.

## References
- https://osv.dev/vulnerability/OSEC-2026-01
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-28364.json
- https://access.redhat.com/security/cve/CVE-2026-28364
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28364.json
- https://github.com/ocaml/security-advisories/blob/generated-osv/2026/OSEC-2026-01.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28364
- https://bugzilla.redhat.com/show_bug.cgi?id=2443348
