# [M] Libkcapi: iv reuse in libkcapi one-shot symmetric cipher chunking causes cipher state reset across chunk boundaries

## Summary
Severity: Medium
Advisory: CVE-2026-71225
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71225
Type: osv

## Details
A flaw was found in libkcapi. When performing one-shot symmetric cipher operations on large inputs (over 64 KiB) in stateful modes such as Counter (CTR) or Cipher Block Chaining (CBC), the library improperly reuses the Initialization Vector (IV) for each internal data chunk. A remote attacker could potentially exploit this by making an application that uses libkcapi process specially crafted large inputs. This can lead to a significant weakening of data confidentiality, as the repeated IV use can expose relationships in encrypted plaintext, and may also affect data integrity by causing incorrect cryptographic processing.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2026:56985
- https://access.redhat.com/security/cve/CVE-2026-71225
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71225.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71225
- https://bugzilla.redhat.com/show_bug.cgi?id=2462011
- https://github.com/smuellerDD/libkcapi
