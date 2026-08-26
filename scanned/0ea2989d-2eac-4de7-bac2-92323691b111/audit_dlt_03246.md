# [M] Excess funds sent via `msg.value` not refunded

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-19
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/358
Type: code-finding

## Details
### Lines of code

--------------

[201](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/Balancer.sol#L201-L212)

### Vulnerability details

-------------

The code below allows the caller to provide Ether, but does not refund the amount in excess of what's required, leaving funds stranded in the contract. The condition should be changed to check for equality, or the code should refund the excess.

```solidity
File: contracts/Balancer.sol

201          bool _isNative = ITapiocaOFT(_srcOft).erc20() == address(0);
202          if (_isNative) {
203              if (msg.value <= _amount) revert FeeAmountNotSet();
204              _sendNative(_srcOft, _amount, _dstChainId, _slippage);
205          } else {
206              if (msg.value == 0) revert FeeAmountNotSet();
207              _sendToken(_srcOft, _amount, _dstChainId, _slippage, _ercData);
208          }
209  
210          connectedOFTs[_srcOft][_dstChainId].rebalanceable -= _amount;
211          emit Rebalanced(_srcOft, _dstChainId, _slippage, _amount, _isNative);
212:     }

```


### Assessed type

------------

other
