# [H] GIMP PGM File Parsing Uninitialized Memory Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-2044
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-20
Source: https://osv.dev/vulnerability/CVE-2026-2044
Type: osv

## Details
GIMP PGM File Parsing Uninitialized Memory Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of GIMP. User interaction is required to exploit this vulnerability in that the target must visit a malicious page or open a malicious file.

The specific flaw exists within the parsing of PGM files. The issue results from the lack of proper initialization of memory prior to accessing it. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-28158.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-2044.json
- https://access.redhat.com/errata/RHSA-2026:4173
- https://access.redhat.com/errata/RHSA-2026:5113
- https://access.redhat.com/errata/RHSA-2026:5388
- https://access.redhat.com/errata/RHSA-2026:5389
- https://access.redhat.com/errata/RHSA-2026:5390
- https://access.redhat.com/errata/RHSA-2026:5391
- https://access.redhat.com/errata/RHSA-2026:5434
- https://access.redhat.com/errata/RHSA-2026:5435
- https://access.redhat.com/errata/RHSA-2026:5436
- https://access.redhat.com/errata/RHSA-2026:5437
- https://access.redhat.com/security/cve/CVE-2026-2044
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2044.json
- https://gitlab.gnome.org/GNOME/gimp/-/merge_requests/2569/diffs?commit_id=112a5e038f0646eae5ae314988ec074433d2b365
- https://nvd.nist.gov/vuln/detail/CVE-2026-2044
- https://www.zerodayinitiative.com/advisories/ZDI-26-118/
- https://bugzilla.redhat.com/show_bug.cgi?id=2441521
