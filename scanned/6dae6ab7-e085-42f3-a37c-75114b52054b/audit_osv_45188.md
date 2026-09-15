# [C] An issue was discovered in GNU gettext 0.19.8

## Summary
Severity: Critical
Advisory: JLSEC-2025-174
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-174
Type: osv

## Affected
- Julia: `Gettext_jll` — affected >=0 <0.20.1+1

## Details
An issue was discovered in GNU gettext 0.19.8. There is a double free in `default_add_message` in read-catalog.c, related to an invalid free in `po_gram_parse` in po-gram-gen.y, as demonstrated by lt-msgfmt.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00061.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00065.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00025.html
- https://access.redhat.com/errata/RHSA-2019:3643
- https://github.com/CCCCCrash/POCs/tree/master/Bin/Tools-gettext-0.19.8.1/doublefree
- https://github.com/CCCCCrash/POCs/tree/master/Bin/Tools-gettext-0.19.8.1/heapcorruption
- https://usn.ubuntu.com/3815-1/
- https://usn.ubuntu.com/3815-2/
