# [M] BIT-bpftool-2021-45941

## Summary
Severity: Medium
Advisory: BIT-bpftool-2021-45941
Aliases: CVE-2021-45941
Ecosystem: Bitnami
Published: 2024-07-01
Source: https://osv.dev/vulnerability/BIT-bpftool-2021-45941
Type: osv

## Affected
- Bitnami: `bpftool` — affected >=0.6.1

## Details
libbpf 0.6.0 and 0.6.1 has a heap-based buffer overflow (8 bytes) in __bpf_object__open (called from bpf_object__open_mem and bpf-object-fuzzer.c).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=40957
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/libbpf/OSV-2021-1576.yaml
