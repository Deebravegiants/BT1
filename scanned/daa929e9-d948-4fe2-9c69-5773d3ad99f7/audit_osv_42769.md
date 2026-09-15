# [H] Libkcapi: memory corruption via uncanceled aio requests on error in libkcapi's one-shot aio path

## Summary
Severity: High
Advisory: CVE-2026-71226
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71226
Type: osv

## Details
Memory Corruption via Uncanceled AIO Requests on Error: libkcapi's one-shot AIO path can return an error before all submitted IOCBs are drained, allowing later kernel writes into caller-owned output buffers.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:56985
- https://access.redhat.com/security/cve/CVE-2026-71226
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71226.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71226
- https://bugzilla.redhat.com/show_bug.cgi?id=2462114
- https://github.com/smuellerDD/libkcapi
