# [C] CVE-2017-15101

## Summary
Severity: Critical
Advisory: CVE-2017-15101
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2017-15101
Type: osv

## Details
A missing patch for a stack-based buffer overflow in findTable() was found in Red Hat version of liblouis before 2.5.4. An attacker could cause a denial of service condition or potentially even arbitrary code execution.

## References
- https://access.redhat.com/errata/RHSA-2017:3384
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-15101
