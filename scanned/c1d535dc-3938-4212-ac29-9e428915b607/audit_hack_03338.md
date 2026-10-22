# [M] [Tomo-M1] Use call instead of transfer when sending ETH

## Summary
Severity: Medium
Reporter: Tomo
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L22-L34
Type: audit-issue

## Details
# [Tomo-M1] Use call instead of transfer when sending ETH

## Summary

Use call instead of transfer when sending ETH

## Vulnerability Detail

The use of the deprecated `transfer()` function for an address will inevitably make the transaction fail when:

1. The claimer smart contract does not implement a payable function.
2. The claimer smart contract does implement a payable fallback which uses more than 2300 gas unit.
3. The claimer smart contract implements a payable fallback function that needs less than 2300 gas units but is called through proxy, raising the call's gas usage above 2300.

Additionally, using higher than 2300 gas might be mandatory for some multisig wallets.

You can see more detail about the risk of using transfer method.

[https://solidity-by-example.org/sending-ether/](https://solidity-by-example.org/sending-ether/)

[https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/](https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/)

## Impact

Using deprecated method leads to unexpected revert for the transaction.

## Code Snippet

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L22-L34](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/lib/UniversalERC20.sol#L22-L34)

```solidity
function universalTransfer(
        IERC20 token,
        address payable to,
        uint256 amount
    ) internal {
        if (amount > 0) {
            if (isETH(token)) {
                to.transfer(amount);
            } else {
                token.safeTransfer(to, amount);
            }
        }
    }
```

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L487-L492](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L487-L492)

```solidity
if (originToToken == _ETH_ADDRESS_) {
            IWETH(_WETH_).withdraw(receiveAmount);
            payable(msg.sender).transfer(receiveAmount);
        } else {
            IERC20(toToken).universalTransfer(payable(msg.sender), receiveAmount);
        }
```

[https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L146-L154](https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L146-L154)

```solidity
function superWithdraw(address token) public onlyOwner {
        if(token != _ETH_ADDRESS_) {
            uint256 restAmount = IERC20(token).universalBalanceOf(address(this));
            IERC20(token).universalTransfer(payable(routeFeeReceiver), restAmount);
        } else {
            uint256 restAmount = address(this).balance;
            payable(routeFeeReceiver).transfer(restAmount);
        }
    }
```

## Tool used

Manual Review

## Recommendation

Use `call()` instead of `transfer()` when transferring ETH
