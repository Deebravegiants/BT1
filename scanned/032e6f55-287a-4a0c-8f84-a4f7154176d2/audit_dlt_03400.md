# [M] Double fee application breaks supply invariant for fee-on-transfer ERC20s

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-11-nibiru
Published: 2024-11-28
Source: https://github.com/code-423n4/2024-11-nibiru-findings/issues/48
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/precompile/funtoken.go#L162-L170


# Vulnerability details

## Finding description and impact

The EVM module incorrectly handles fee-on-transfer tokens when converting bank coins back to ERC20s, resulting in unbacked bank coins remaining in circulation. This breaks the intended 1:1 supply tracking invariant between ERC20 tokens and their bank coin representations.

When converting from ERC20 to bank coins via `sendToBank`, the code correctly accounts for transfer fees by only minting bank coins equal to the amount actually received. However, when converting these bank coins back to ERC20s via `convertCoinToEvmBornERC20`, the code:
1. Takes in X bank coins from the user
2. Tries to transfer X ERC20 tokens
3. Due to fees, only Y tokens are received (Y < X)
4. Only burns Y bank coins

This creates a discrepancy since the original conversion already accounted for fees. The transfer fees are effectively applied twice:
1. First fee: 100 ERC20 -> 95 bank coins (correct)
2. Second fee: 95 bank coins -> ~90.25 ERC20 (and only burn 90.25 bank coins)
   
This leaves 4.75 unbacked bank coins in circulation (95 - 90.25), as the code only burns what was actually transferred in the second conversion.

The impact is monetary - it creates unbacked bank coins that can be used in the rest of the system but don't have corresponding ERC20 tokens backing them in the EVM module's account. Over time, this could lead to significant supply inflation of the bank coin representation.

## Proof of Concept

The first conversion correctly handles fees in `funtoken.go`:

```go
// First conversion correctly uses actual received amount
gotAmount, transferResp, err := p.evmKeeper.ERC20().Transfer(erc20, caller, transferTo, amount, ctx)
if err != nil {
    return nil, fmt.Errorf("error in ERC20.transfer from caller to EVM account: %w", err)
}
coinToSend := sdk.NewCoin(funtoken.BankDenom, math.NewIntFromBigInt(gotAmount))
```
[Link to code](https://github.com/code-423n4/2024-11-nibiru/blob/84054a4f00fdfefaa8e5849c53eb66851a762319/x/evm/precompile/funtoken.go#L162-L170)

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-11-nibiru-findings/issues/48_
