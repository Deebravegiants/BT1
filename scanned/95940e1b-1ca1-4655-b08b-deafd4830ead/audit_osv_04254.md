# [M] BIT-bpftool-2025-29481

## Summary
Severity: Medium
Advisory: BIT-bpftool-2025-29481
Aliases: CVE-2025-29481
Ecosystem: Bitnami
Published: 2025-04-16
Source: https://osv.dev/vulnerability/BIT-bpftool-2025-29481
Type: osv

## Affected
- Bitnami: `bpftool` — affected >=1.5.0 <7.4.0

## Details
Buffer Overflow vulnerability in libbpf 1.5.0 allows a local attacker to execute arbitrary code via the bpf_object__init_prog` function of libbpf. This has been disputed by third parties who assert that "no one in their sane mind should be passing untrusted ELF files into libbpf while running under root."

## References
- https://github.com/lmarch2/poc/blob/main/libbpf/libbpf.md
- https://nvd.nist.gov/vuln/detail/CVE-2025-29481
