# [M] Base tokens accumulated from withdraw fees can't be transferred to/from the NoyaFeeReceiver and will remain stuck

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1287
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/NoyaFeeReceiver.sol#L23-L30


# Vulnerability details

## Impact
Different instances of the NoyaFeeReceiver will collect the different fees, and they're all based upon the NoyaFeeReceiver:

- ManagementFeeReceiver
- PerformanceFeeReceiver
- WithdrawFeeReceiver

Although the management and the performance fees are shares which are minted directly to the mint receiver, the withdraw fees are sent as the base token.

Within the NoyaFeeReceiver there is no way to transfer the base tokens sent to it ,as well as it doesn't implement/import any ERC20 interfaces, causing the sent base tokens to the contract to remain in the contract with no way to take them out.

## Proof of Concept
Whenever withdraw fees are collected, they're stored and sent to the withdrawFeeReceiver after the withdraw group's withdrawal execution has finished:

```
  processedBaseTokenAmount += data.amount;
            {
                uint256 feeAmount = baseTokenAmount * withdrawFee / FEE_PRECISION;
                withdrawFeeAmount += feeAmount;
                baseTokenAmount = baseTokenAmount - feeAmount;
            }

...

  if (withdrawFeeAmount > 0) {
            baseToken.safeTransfer(withdrawFeeReceiver, withdrawFeeAmount);
        }

```

Unlike most other fee collection mechanisms where the fees are minted as shares to the different fee receivers:

```
  _mint(performanceFeeReceiver, preformanceFeeSharesWaitingForDistribution);
```

The NoyaFeeReceiver is only equipped to handle fee collection in the form of shares, due to only having two functions, one to burn shares and the other to "withdraw" the shares as base tokens and send them directly to a third party named "receiver":

```
   function withdrawShares(uint256 amount) external onlyOwner {
        AccountingManager(accountingManager).withdraw(amount, receiver);
    }

    function burnShares(uint256 amount) external onlyOwner {
        AccountingManager(accountingManager).burnShares(amount);
    }
```

Since there's no way for any tokens sent to this contract to be retrieved, they will be stuck in the contract, i.e. the fee receiver is not equipped to handle the fees in the form of base/underlying tokens. 

## Tools Used
Manual Review

## Recommended Mitigation Steps
Integrate ERC20 transfer functionalities within the NoyaFeeReceiver.


## Assessed type

Token-Transfer
