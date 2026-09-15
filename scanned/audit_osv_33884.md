# [H] Icu: stack buffer overflow in the srbroot::addtag function

## Summary
Severity: High
Advisory: CVE-2025-5222
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/CVE-2025-5222
Type: osv

## Details
A stack buffer overflow was found in Internationl components for unicode (ICU ). While running the genrb binary, the 'subtag' struct overflowed at the SRBRoot::addTag function. This issue may lead to memory corruption and local arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://cert-portal.siemens.com/productcert/html/ssa-585531.html
- https://lists.debian.org/debian-lts-announce/2025/06/msg00015.html
- https://unicode-org.atlassian.net/
- https://unicode-org.atlassian.net/jira/software/c/projects/ICU/issues/ICU-22957
- https://access.redhat.com/errata/RHSA-2025:11888
- https://access.redhat.com/errata/RHSA-2025:12083
- https://access.redhat.com/errata/RHSA-2025:12331
- https://access.redhat.com/errata/RHSA-2025:12332
- https://access.redhat.com/errata/RHSA-2025:12333
- https://access.redhat.com/errata/RHSA-2026:54544
- https://access.redhat.com/errata/RHSA-2026:54553
- https://access.redhat.com/errata/RHSA-2026:54581
- https://access.redhat.com/errata/RHSA-2026:56786
- https://access.redhat.com/errata/RHSA-2026:56853
- https://access.redhat.com/errata/RHSA-2026:56911
- https://access.redhat.com/errata/RHSA-2026:60019
- https://access.redhat.com/security/cve/CVE-2025-5222
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5222.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5222
