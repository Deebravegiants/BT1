# [C] CVE-2020-27743

## Summary
Severity: Critical
Advisory: CVE-2020-27743
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-26
Source: https://osv.dev/vulnerability/CVE-2020-27743
Type: osv

## Details
libtac in pam_tacplus through 1.5.1 lacks a check for a failure of RAND_bytes()/RAND_pseudo_bytes(). This could lead to use of a non-random/predictable session_id.

## References
- https://github.com/kravietz/pam_tacplus/pull/163
- https://tools.ietf.org/html/rfc8907
