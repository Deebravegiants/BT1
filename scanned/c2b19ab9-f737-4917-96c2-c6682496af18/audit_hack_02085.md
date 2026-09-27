# [M] 7.5 Unclear Parameter Specification

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Specification Changed

There are several input parameters to each call. These are passed in three different structs:
ExchangeData, CdpData, AddressRegistry. Some definitions of the parameters of the strucs are
unclear and may lead to mistakes.

- borrowCollateral is specified to be the collateral to buy with the flashloan in increase
    operations. However, it is used differently. More precisely, it is used in function _decreaseMP to
    specify how much collateral to be withdrawn from the vault. The frontend may create mistakes. If the
    intention of borrowCollateral is to be used as the amount that will be, together with
    depositCollateral, deposited to the vault, then with positive slippage, joinDrawDebt would
    deposit too much collateral into the vault.
- depositCollateral is specified to be the amount of collateral the user deposits in increase
    actions that deposit collateral. For ETH that is not the case since msg.value is used and no check
    if it equals depositCollateral is done. The call will work but the result may differ from the
    expected behaviour.
- fromTokenAmount is specified to be the amount of tokens to be exchanged. depositDai is the
    amount of DAI that should be exchanged jointly with the flashloaned DAI in increase operations. In
    _increaseMP in the call to swap the tokens to collateral, the to be swapped amount is specified as
    the sum of fromTokenAmount and depositDAI. However, according to specification,
    fromTokenAmount should already be accounting for the deposit.
- Depending on what the intended use of the parameters is, specifying invariants could be helpful to
    clarify for example whether the fromTokenAmount in increase operations is the sum of the
    flashloaned and deposited DAI.

Clarifying these and similar ambiguities may help users to understand the parameters of their
transactions better.

Specification changed:

The parameters are now more precisely defined.
