# [M] 5.3.2 uncheckedmay cause under/overflows

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** LienToken.sol#L424, LienToken.sol#L482, PublicVault.sol#L376, PublicVault.sol#L422, Public-
Vault.sol#L439, PublicVault.sol#L490, PublicVault.sol#L578, PublicVault.sol#L611, PublicVault.sol#L527,
PublicVault.sol#L544, PublicVault.sol#L563, PublicVault.sol#L640, VaultImplementation.sol#L401,
WithdrawProxy.sol#L254, WithdrawProxy.sol#L293
**Description:** uncheckedshould only be used when there is a guarantee of no underflows or overflows, or when
they are taken into account. In absence of certainty, it's better to avoiduncheckedto favor correctness over gas
efficiency.
For instance, if by error,protocolFeeNumeratoris set to be greater thanprotocolFeeDenominator, this block in
_handleProtocolFee()will underflow:
unchecked {
amount -= fee;
}

However, later this reverts due to the ERC20 transfer of an unusually high amount. This is just to demonstrate that
unknown bugs can lead to under/overflows.
**Recommendation:** Reason about eachuncheckedand remove them in absence of absolute certainty of safety.
**Astaria:** Acknowledged. We'll put checks on setting protocol values to not cross unintended boundaries.
**Spearbit:** Acknowledged.
