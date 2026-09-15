# [C] CVE-2026-33278

## Summary
Severity: Critical
Advisory: CVE-2026-33278
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-33278
Type: osv

## Details
NLnet Labs Unbound 1.19.1 up to and including version 1.25.0 has a vulnerability in the DNSSEC validator that enables denial of service and possible remote code execution as a result of deep copying a data structure and erroneously overwriting a destination pointer. An adversary can exploit the vulnerability by controlling a malicious signed zone and querying a vulnerable Unbound. When DS sub-queries need to suspend validation due to NSEC3 computational budget exhaustion (introduced in Unbound 1.19.1), Unbound deep-copies response messages to preserve them across memory region teardown. A struct-assignment bug overwrites the destination's pointer with the source's pointer. After the sub-query region is freed, the resumed validator dereferences this dangling pointer, triggering a crash or potentially enabling arbitrary code execution. Unbound 1.25.1 contains a patch with a fix to preserve the correct pointer when deep copying the data structure.

## References
- https://access.redhat.com/security/cve/CVE-2026-33278
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33278.json
- https://access.redhat.com/errata/RHSA-2026:19752
- https://access.redhat.com/errata/RHSA-2026:23231
- https://access.redhat.com/errata/RHSA-2026:24369
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-33278.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2479808
