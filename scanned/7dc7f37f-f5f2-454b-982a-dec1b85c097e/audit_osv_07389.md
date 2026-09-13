# [C] BIT-pytorch-2024-48063

## Summary
Severity: Critical
Advisory: BIT-pytorch-2024-48063
Aliases: CVE-2024-48063, PYSEC-2024-259
Ecosystem: Bitnami
Published: 2025-07-16
Source: https://osv.dev/vulnerability/BIT-pytorch-2024-48063
Type: osv

## Affected
- Bitnami: `pytorch` — affected >=0 <2.5.0

## Details
In PyTorch <=2.4.1, the RemoteModule has Deserialization RCE. NOTE: this is disputed by multiple parties because this is intended behavior in PyTorch distributed computing.

## References
- https://gist.github.com/hexian2001/c046c066895a963ecc0a2cf9e1180065
- https://github.com/pytorch/pytorch/issues/129228
- https://github.com/pytorch/pytorch/security/policy#using-distributed-features
- https://nvd.nist.gov/vuln/detail/CVE-2024-48063
- https://rumbling-slice-eb0.notion.site/Distributed-RPC-Framework-RemoteModule-has-Deserialization-RCE-in-pytorch-pytorch-111e3cda9e8c8021a7d3cbc61ee1a20c
