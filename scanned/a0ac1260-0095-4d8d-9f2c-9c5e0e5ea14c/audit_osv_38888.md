# [H] CVE-2026-42959

## Summary
Severity: High
Advisory: CVE-2026-42959
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-42959
Type: osv

## Details
NLnet Labs Unbound up to and including version 1.25.0 has a denial of service vulnerability in the DNSSEC validator that can lead to a crash given malicious upstream replies. When Unbound constructs chase-reply messages for validation, the code uses the wrong counter to calculate write offsets for ADDITIONAL section rrsets. DNAME duplication could increase the ANSWER section count and authority filtering could decrease the AUTHORITY section count and create an uninitialized array slot. Combining these two, the validator later dereferences this uninitialized pointer, causing an immediate process crash. An adversary controlling a DNSSEC-signed domain can trigger this bug with a single query by configuring a DNAME chain with unsigned CNAMEs and a response containing unsigned AUTHORITY records alongside signed ADDITIONAL glue records. Unbound 1.25.1 contains a patch with a fix to use the proper counters to calculate the write offsets.

## References
- https://access.redhat.com/security/cve/CVE-2026-42959
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42959.json
- https://access.redhat.com/errata/RHSA-2026:19752
- https://access.redhat.com/errata/RHSA-2026:23231
- https://access.redhat.com/errata/RHSA-2026:24365
- https://access.redhat.com/errata/RHSA-2026:24369
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-42959.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2479806
