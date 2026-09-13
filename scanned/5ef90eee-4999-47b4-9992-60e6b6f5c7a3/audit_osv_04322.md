# [M] Consul-template vulnerable to sandbox path bypass in file helper via a symlink attack

## Summary
Severity: Medium
Advisory: BIT-consul-2026-5061
Aliases: CVE-2026-5061
Ecosystem: Bitnami
Published: 2026-05-14
Source: https://osv.dev/vulnerability/BIT-consul-2026-5061
Type: osv

## Affected
- Bitnami: `consul` — affected >=0.1.0 <0.42.0

## Details
The consul-template library before version 0.42.0 is vulnerable to a sandbox path bypass in the file template helper that may allow reading an out-of-sandbox file. This vulnerability (CVE-2026-5061) is fixed in consul-template 0.42.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-12-consul-template-vulnerable-to-sandbox-path-bypass-in-file-helper-through-symlink-attack/77414
- https://nvd.nist.gov/vuln/detail/CVE-2026-5061
