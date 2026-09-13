# [H] zAuction - incomplete / dead code `zWithdraw` and `zDeposit`

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

The code generally does not appear to be production-ready. The methods `zWithdraw` and `zDeposit` do not appear to be properly implemented. `zWithdraw` rather burns `ETH` balance than withdrawing it for an account (missing transfer) and `zDeposit` manipulates an accounts balance but never receives the `ETH` amount it credits to an account.

#### Examples


**zAuction/contracts/zAuctionAccountant.sol:L44-L52**
```solidity
    function zDeposit(address to) external payable onlyZauction {
        ethbalance[to] = SafeMath.add(ethbalance[to], msg.value);
        emit zDeposited(to, msg.value);
    }

    function zWithdraw(address from, uint256 amount) external onlyZauction {
        ethbalance[from] = SafeMath.sub(ethbalance[from], amount);
        emit zWithdrew(from, amount);
    }
```

#### Recommendation

The methods do not seem to be used by the zAuction contract. It is highly discouraged from shipping incomplete implementations in productive code. Remove dead/unreachable code. Fix the implementations to perform proper accounting before reintroducing them if they are called by zAuction.
