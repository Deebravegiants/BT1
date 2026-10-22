# [M] GMXFuturesPoolHedger uses payable.transfer

## Summary
Severity: Medium
Contest weight: 0.5570
Dataset id: 19700
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ETH transfers are done with payable(msg.sender).transfer, which can malfunction
for smart contract receivers.
This is unsafe as transfer has hard coded gas budget and can fail when msg.sender
is a smart contract. Such transactions will fail for smart contract users which don't
fit to 2300 gas stipend transfer have.
The issues with transfer() are outlined here:
https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/
Funds will be unattainable for smart contract receivers.
payable(msg.sender).transfer is used for an arbitrary msg.sender:
oolHedger.sol#L284-L287
```solidity
_hedgeDelta(expectedHedge);
// return any excess eth
payable(msg.sender).transfer(address(this).balance);
}
```
oolHedger.sol#L329-L332
```solidity
emit CollateralOrderPosted(pendingOrderKey, positions.isLong, collateralDelta);
// return any excess eth
payable(msg.sender).transfer(address(this).balance);
}
```

## Recommendation
The recommendation is to use low-level call.value(amount) with the
corresponding result check or employ OpenZeppelin's Address.sendValue:
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Address.sol#L60
