# [M] rescueERC20 May Return False Positive (true on failure)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/43
Type: sherlock-finding

## Details
0xAgro

medium

# rescueERC20 May Return False Positive (true on failure)

## Summary
The honesty of the protocol is impacted by an unsafe `transfer` in `/contracts/fee-buyback/FeeBuyback.sol` [L94-L97](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97). A comment on the `rescueERC20` function states: "*@return boolean value indicating whether the operation succeeded*". This statement will not always be the case and `rescueERC20` may report false positives if an ERC20 returns `false` in it's `transferFrom` function rather than reverting (which is the case in [Telcoin's supported coins](https://tokenlists.org/token-list?url=https://raw.githubusercontent.com/telcoin/token-lists/master/telcoins.json)). This may give an attacker an extra edge in the likelihood of them stealing more ERC20 funds if a draining exploit is found.

**Medium Justification**
I do not believe this is a high-severity vulnerability as it (to my knowledge) would not allow a standard user to steal funds.

I believe that this vulnerability can act as an exploit amplifier. It can result in the increased odds of permanent loss of funds from a "reasonable protocol team" (from [medium definition](https://docs.sherlock.xyz/audits/watsons/judging)).

## Vulnerability Detail

Not all ERC20 contract `transfer` functions revert on failure, some return `false`. 

Below is an example of the [STASIS EURO](https://etherscan.io/address/0xdB25f211AB05b1c97D595516F45794528a807ad8#code) `transfer` function (a [supported token](https://tokenlists.org/token-list?url=https://raw.githubusercontent.com/telcoin/token-lists/master/telcoins.json)) which returns `false` on error.
```solidity
function transfer (address _to, uint256 _value)
  public delegatable payable returns (bool) {
    if (frozen) return false;
    else if (
      (addressFlags [msg.sender] | addressFlags [_to]) & BLACK_LIST_FLAG ==
      BLACK_LIST_FLAG)
      return false;
    else {
      uint256 fee =
        (addressFlags [msg.sender] | addressFlags [_to]) & ZERO_FEE_FLAG == ZERO_FEE_FLAG ?
          0 :
          calculateFee (_value);

      if (_value <= accounts [msg.sender] &&
          fee <= safeSub (accounts [msg.sender], _value)) {
        require (AbstractToken.transfer (_to, _value));
        require (AbstractToken.transfer (feeCollector, fee));
        return true;
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/43_
