# [H] Integer overflow in solana_rbpf

## Summary
Severity: High
Chain: solana_rbpf
Component: solana_rbpf
CVE: CVE-2021-46102
CWE: Integer Overflow or Wraparound
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-xwqr-xmgg-j69q
Type: github-advisory

## Details
From version 0.2.14 to 0.2.16 for Solana rBPF, function "relocate" in the file src/elf.rs has an integer overflow bug because the sym.st_value is read directly from ELF file without checking. If the sym.st_value is rather large, an integer overflow is triggered while calculating the variable "addr" via `addr = (sym.st_value + refd_pa) as u64`
