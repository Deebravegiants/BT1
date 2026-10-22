# [M] MoneyMon incident: The LegendaryMoneyMonNft contract’s cliamRewred function had a signature verification flaw. The verify() only checked if recoverSi

## Summary
Severity: Medium
Target: MoneyMon
Loss: $ 85,519.47
Attack method: Smart Contract Vulnerability
Published: 2026-05-29
Source: https://x.com/SlowMist_Team/status/2060205558687486441
Type: slowmist-incident

## Details
The LegendaryMoneyMonNft contract’s cliamRewred function had a signature verification flaw. The verify() only checked if recoverSigner(...) == admin, without properly validating cases where ecrecover returns address(0). The attacker set admin to zero address, then used an invalid signature (r=0, s=0, v=27) to bypass checks, arbitrarily claim rewards, drain all tokens from the contract, and swap them for USDT via PancakeSwap.
