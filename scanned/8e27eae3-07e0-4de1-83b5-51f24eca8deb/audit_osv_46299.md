# [H] JLSEC-2026-99

## Summary
Severity: High
Advisory: JLSEC-2026-99
Ecosystem: Julia
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/JLSEC-2026-99
Type: osv

## Affected
- Julia: `Deno_jll` — affected >=1.10.3+0 <1.14.3+0

## Details
Deno <=1.14.0 file sandbox does not handle symbolic links correctly. When running Deno with specific write access, the Deno.symlink method can be used to gain access to any directory.

## References
- https://github.com/denoland/deno/issues/12152
- https://hackers.report/report/614876917a7b150012836bb8
