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
      } else return false;
    }
  }
```


On [line 95](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L95) of  `/contracts/fee-buyback/FeeBuyback.sol` (seen below) if the ERC20 transfer did not occur and `false` is returned the `rescueERC20` function will still return `true`. This will result in a false positive making the rescuer believe the funds have been saved yet they could still be locked.

## Impact

in a high-stress scenario like a hack, if the code base was exploited requiring the team to quickly move funds of a specific token the `rescueERC20` function may indicate a move was successful when it was not. In a separate hypothetical draining attack, an exploiter could use the false positive to their advantage and target ERC20s that do not revert in their `transfer` functions last increasing the odds of a team thinking tokens got transferred when they didn't. This would increase the chances of more funds being stolen.

Any future use of the `rescueERC20` function that assumed validity will also be affected perhaps resulting in further exploits until fixed.

## Code Snippet

File: `/contracts/fee-buyback/FeeBuyback.sol`
Function: `rescueERC20`
Line(s): [L94-L97](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L94-L97)
```solidity
94:function rescueERC20(address account, address externalToken, uint256 amount) public onlyExecutor() returns (bool) {
95:	IERC20(externalToken).transfer(account, amount);
96:	return true;
97:}
```

## Tool used

Manual Review

## Recommendation

Check the return value of `transfer`.

Duplicate of #82
