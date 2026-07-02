# Q1603: receiveFromNodeDelegator Fee On Transfer Token Skew Withdrawal Liquidity ETHx P1603

## Question
Can an unprivileged ETH sender enter through `external payable receiveFromNodeDelegator()` while controlling msg.value and timing relative to getTotalAssetDeposits and use a supported ERC20 path where received balance is lower than depositAmount or transfer amount, causing `contracts/LRTDepositPool.sol::receiveFromNodeDelegator` to break the invariant that minted rsETH and committed withdrawals are based on actual assets received; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator, leading to failure to deliver promised returns without principal loss? Probe condition: ETHx supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.

## Target
- File/function: contracts/LRTDepositPool.sol::receiveFromNodeDelegator
- Entrypoint: external payable receiveFromNodeDelegator()
- Attacker controls: msg.value and timing relative to getTotalAssetDeposits; scenario: use a supported ERC20 path where received balance is lower than depositAmount or transfer amount; validation style: an attacker contract as msg.sender or recipient; probe condition: ETHx supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller
- Exploit idea: Use receiver contract path to exercise the fee-on-transfer token skew path against receiveFromNodeDelegator and look for withdrawal liquidity breaking value conservation or liveness.
- Invariant to test: minted rsETH and committed withdrawals are based on actual assets received; specifically, withdrawal liquidity must not violate backing, queue, yield, or liquidity accounting for receiveFromNodeDelegator
- Expected Immunefi impact: Low. Contract fails to deliver promised returns, but doesn't lose value
- Fast validation: assert user-created demand cannot strand unrelated users by consuming liquidity accounting Use probe condition: ETHx supported asset route; amount case 1 wei; timing at withdrawalDelayBlocks plus 1; caller model EOA caller.
