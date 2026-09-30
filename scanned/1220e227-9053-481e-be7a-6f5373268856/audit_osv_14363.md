# [C] CVE-2018-9838

## Summary
Severity: Critical
Advisory: CVE-2018-9838
Aliases: OSEC-2018-01
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-06
Source: https://osv.dev/vulnerability/CVE-2018-9838
Type: osv

## Details
The caml_ba_deserialize function in byterun/bigarray.c in the standard library in OCaml 4.06.0 has an integer overflow which, in situations where marshalled data is accepted from an untrusted source, allows remote attackers to cause a denial of service (memory corruption) or possibly execute arbitrary code via a crafted object.

## References
- https://security.gentoo.org/glsa/202007-48
- https://caml.inria.fr/mantis/view.php?id=7765
