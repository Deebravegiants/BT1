# [?] core/vm: fix overflow in EIP 2929 gas calculation (#433)

## Summary
Severity: Unknown
Chain: Ronin
Component: axieinfinity/ronin
Published: 2024-04-05
Source: https://github.com/axieinfinity/ronin-archive/commit/db3003996ba6bf65461bc99427c995dd43eefd51
Type: security-commit

## Details
core/vm: fix overflow in EIP 2929 gas calculation (#433)

This partially cherry-picks the commit
https://github.com/ethereum/go-ethereum/commit/ac0ff044606a663eeb47ef60ed5506f842753084
to add the overflow check when doing gas calculation in EIP 2929.
