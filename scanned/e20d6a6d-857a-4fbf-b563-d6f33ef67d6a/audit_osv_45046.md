# [M] Path traversal in Cohttp.Path.resolve_local_file

## Summary
Severity: Medium
Advisory: OSEC-2026-16
Ecosystem: opam
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/S:N/AU:Y/R:A/V:D/RE:M)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/OSEC-2026-16
Type: osv

## Affected
- opam: `cohttp` — affected >=0 <6.3.0, >=0 <5f5a65ec3289c1cd8072bdf0ef22c181b4f11356

## Details
The issue is that the function normalizes the URI path before percent
decoding it:

```OCaml
let resolve_local_file ~docroot ~uri =

  let path = Uri.(pct_decode (path (resolve "http" (of_string "/") uri))) in

  ...
```

Because `%2f` is decoded after Uri.resolve, encoded separators survive
dot-segment normalization. For example, a request path like:

```
/static/..%2f..%2f..%2fetc/passwd
```

is normalized as a single encoded segment, then decoded into:

```
/static/../../../etc/passwd
```

afterwards.

## Timeline

- Aug 11th 2026: report to security@ocaml.org
- Aug 14th 2026: PR published on <https://github.com/mirage/ocaml-cohttp/pull/1145>
- Aug 20th 2026: fix released in v6.3.0 <https://github.com/ocaml/opam-repository/pull/30528>
