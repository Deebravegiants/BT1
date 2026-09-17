# [M] Merchant address can be null

## Summary
Severity: Medium
Source: https://github.com/ChainXcom/coinfix.io-smart-contracts/blob/75edd659ce96c88fe2784f3e767d6617787e8b7c/merchant%5Fsubscription/MerchantSubscription.sol#L83
Type: audit-issue

## Details
A [MerchantSubscription](https://github.com/ChainXcom/coinfix.io-smart-contracts/blob/75edd659ce96c88fe2784f3e767d6617787e8b7c/merchant%5Fsubscription/MerchantSubscription.sol#L83) contract can be instantiated with the null address as the `merchant` parameter. Such an instance will never be able to be activated or function at all. Consider adding a sanity check in the constructor to require that the `merchant` parameter is different from `0x0`. This will also be in line with the principle of [failing as early and loudly as possible](https://blog.zeppelin.solutions/onward-with-ethereum-smart-contract-security-97a827e47702#14aa).  
_**Update:** Fixed in [this](https://github.com/ChainXcom/coinfix.io-smart-contracts/commit/c02c083173fee08fb6e8e20ff854e5fbbbe9ed55) commit by checking `merchant != 0x0`._
