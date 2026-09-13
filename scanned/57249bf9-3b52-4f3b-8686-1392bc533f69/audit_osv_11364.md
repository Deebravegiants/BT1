# [H] CVE-2017-7537

## Summary
Severity: High
Advisory: CVE-2017-7537
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-7537
Type: osv

## Details
It was found that a mock CMC authentication plugin with a hardcoded secret was accidentally enabled by default in the pki-core package before 10.6.4. An attacker could potentially use this flaw to bypass the regular authentication process and trick the CA server into issuing certificates.

## References
- https://access.redhat.com/errata/RHSA-2017:2335
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7537
- https://github.com/dogtagpki/pki/commit/876d13c6d20e7e1235b9
