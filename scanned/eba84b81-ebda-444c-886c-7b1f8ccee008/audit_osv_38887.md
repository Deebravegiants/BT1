# [H] CVE-2026-42944

## Summary
Severity: High
Advisory: CVE-2026-42944
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/CVE-2026-42944
Type: osv

## Details
NLnet Labs Unbound 1.14.0 up to and including version 1.25.0 has a vulnerability that results in heap overflow when encoding multiple NSID and/or DNS Cookie EDNS and/or EDNS Padding options in the reply packet. The relevant options ('nsid', 'answer-cookie', 'pad-responses' (default)) need to be enabled for the vulnerability to be exploited. An adversary who can query Unbound can exploit the vulnerability by attaching multiple NSID and/or DNS Cookie EDNS and/or EDNS Padding options to the query. A flaw in the size calculation of the EDNS field truncates the correct value which allows the encoder to overflow the available space when writing. Those two combined lead to a heap overflow write of Unbound controlled data and eventually a crash. Unbound 1.25.1 contains a patch with a fix to de-duplicate the EDNS options and a fix to prevent truncation of the EDNS field size calculation.

## References
- https://access.redhat.com/security/cve/CVE-2026-42944
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42944.json
- https://access.redhat.com/errata/RHSA-2026:19752
- https://access.redhat.com/errata/RHSA-2026:23231
- https://access.redhat.com/errata/RHSA-2026:24365
- https://access.redhat.com/errata/RHSA-2026:24369
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2026-42944.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2479774
