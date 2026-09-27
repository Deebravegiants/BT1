# [C] CVE-2017-9772

## Summary
Severity: Critical
Advisory: CVE-2017-9772
Aliases: OSEC-2017-01
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-23
Source: https://osv.dev/vulnerability/CVE-2017-9772
Type: osv

## Details
Insufficient sanitisation in the OCaml compiler versions 4.04.0 and 4.04.1 allows external code to be executed with raised privilege in binaries marked as setuid, by setting the CAML_CPLUGINS, CAML_NATIVE_CPLUGINS, or CAML_BYTE_CPLUGINS environment variable.

## References
- http://www.securityfocus.com/bid/99277
- https://security.gentoo.org/glsa/201710-07
- https://caml.inria.fr/mantis/view.php?id=7557
- https://sympa.inria.fr/sympa/arc/caml-list/2017-06/msg00094.html
