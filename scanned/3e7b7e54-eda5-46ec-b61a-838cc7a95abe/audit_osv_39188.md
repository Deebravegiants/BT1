# [H] FreeRDP RDPEAR NDR ref-id aliasing causes client-side UAF/double-free and type confusion

## Summary
Severity: High
Advisory: CVE-2026-44422
Aliases: GHSA-j9q5-7g8m-jc9v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44422
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to 3.26.0, FreeRDP's RDPEAR NDR parser accepts one non-null NDR pointer ref-id for multiple logical pointer fields without tracking the pointed object's expected NDR type or ownership. When the same ref-id is reused across two pointer fields, the parser assigns the same heap object to both output fields. The generic destructor later walks each field independently and destroys/frees both pointers. This causes a malicious-server-triggerable heap use-after-free / double-free in the FreeRDP client's RDPEAR authentication-redirection path. This vulnerability is fixed in 3.26.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44422.json
- https://access.redhat.com/errata/RHSA-2026:36203
- https://access.redhat.com/errata/RHSA-2026:46393
- https://access.redhat.com/security/cve/CVE-2026-44422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44422.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-j9q5-7g8m-jc9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-44422
- https://bugzilla.redhat.com/show_bug.cgi?id=2483467
