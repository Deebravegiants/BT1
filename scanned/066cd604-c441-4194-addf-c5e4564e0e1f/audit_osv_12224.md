# [M] CVE-2018-10932

## Summary
Severity: Medium
Advisory: CVE-2018-10932
CVSS: 4.3 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-10932
Type: osv

## Details
lldptool version 1.0.1 and older can print a raw, unsanitized attacker controlled buffer when mngAddr information is displayed. This may allow an attacker to inject shell control characters into the buffer and impact the behavior of the terminal.

## References
- https://access.redhat.com/errata/RHSA-2019:3673
- https://github.com/intel/openlldp/pull/7
- https://bugzilla.redhat.com/show_bug.cgi?id=1551623
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10932
