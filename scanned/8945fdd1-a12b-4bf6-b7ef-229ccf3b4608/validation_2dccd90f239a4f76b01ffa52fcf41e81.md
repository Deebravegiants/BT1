### Title
ETH Sent Directly to `LRTConverter` Has No Rescue Path and Becomes Temporarily Frozen - (File: contracts/LRTConverter.sol)

### Summary
`LRTConverter` accepts ETH from any caller via its unrestricted `receive()` function but provides no standalone ETH rescue or withdrawal function. ETH that lands in the contract through any path other than a Lido/Swell claim is frozen until an operator happens to call `claimStEth()` or `claimSwEth()`, and if no such claim is ever triggered again, the ETH is permanently irrecoverable.

### Finding Description
`LRTConverter` declares an open `receive()` function: [1](#0-0) 

The only two code paths that move ETH out of the contract are `claimStEth()` and `claimSwEth()`, both of which are restricted to `onlyLRTOperator` and both of which call the internal helper `_sendEthToDepositPool(address(this).balance)`: [2](#0-1) [3](#0-2) 

`_sendEthToDepositPool` forwards the entire native balance to the deposit pool and simultaneously decrements `ethValueInWithdrawal`: [4](#0-3) 

There is no `rescueETH`, no `transferETH`, and no other function that can move ETH out of `LRTConverter` independently of a claim lifecycle. Any ETH that arrives via the bare `receive()` hook — whether from a mistaken user transfer, a refund from an external protocol, or any other source — is trapped inside the contract until an operator initiates and completes a new stETH or swETH unstake cycle.

### Impact Explanation
ETH sent directly to `LRTConverter` is frozen for an indefinite period. If the protocol has already completed all outstanding Lido/Swell withdrawals and no new unstaking is queued, the ETH has no exit path and is permanently locked. Even in the normal case, the ETH is inaccessible to its sender and cannot be recovered without operator intervention. Additionally, when the ETH is eventually swept out via `_sendEthToDepositPool(address(this).balance)`, the accidentally deposited ETH inflates the amount subtracted from `ethValueInWithdrawal`, understating the converter's tracked withdrawal value and distorting the TVL reported by `getETHDistributionData()` in `LRTDepositPool`: [5](#0-4) 

**Impact: Medium — Temporary (potentially permanent) freezing of funds.**

### Likelihood Explanation
Any external caller — a user who mistakenly sends ETH to the contract address, an external protocol that refunds ETH, or a bridge that delivers ETH — can trigger this condition with a single transaction. The `receive()` function imposes no restrictions. The scenario is realistic and requires no privileged access.

### Recommendation
Add a `rescueETH()` function analogous to the existing `rescueERC20()` pattern used elsewhere in the codebase (see `Recoverable.sol`):

```solidity
function rescueETH(address recipient, uint256 amount) external onlyLRTAdmin {
    UtilLib.checkNonZeroAddress(recipient);
    (bool success,) = payable(recipient).call{value: amount}("");
    if (!success) revert EthTransferFailed();
    emit EthRescued(recipient, amount);
}
```

Alternatively, restrict the `receive()` function to only accept ETH from the Lido withdrawal queue and the Swell exit contract, rejecting all other senders.

### Proof of Concept
1. Deploy the protocol normally with `LRTConverter` configured.
2. A user mistakenly calls `address(lrtConverter).call{value: 1 ether}("")` — the `receive()` function accepts it silently.
3. No `claimStEth()` or `claimSwEth()` is pending or scheduled.
4. The 1 ETH is now locked in `LRTConverter` with no callable function to retrieve it.
5. `ethValueInWithdrawal` remains unchanged, so `getETHDistributionData()` does not account for the stranded ETH, and the TVL is misreported.
6. If the operator eventually calls `claimStEth()` for an unrelated withdrawal, `_sendEthToDepositPool(address(this).balance)` sweeps the stranded ETH along with the claim proceeds, over-decrementing `ethValueInWithdrawal` and permanently distorting the accounting.

### Citations

**File:** contracts/LRTConverter.sol (L117-118)
```text
    /// @dev fallback to receive funds
    receive() external payable { }
```

**File:** contracts/LRTConverter.sol (L180-183)
```text
    function claimStEth(uint256 _requestId, uint256 _hint) external nonReentrant onlyLRTOperator {
        _claimStEth(_requestId, _hint);
        _sendEthToDepositPool(address(this).balance);
    }
```

**File:** contracts/LRTConverter.sol (L191-194)
```text
    function claimSwEth(uint256 _tokenId) external nonReentrant onlyLRTOperator {
        _claimSwEth(_tokenId);
        _sendEthToDepositPool(address(this).balance);
    }
```

**File:** contracts/LRTConverter.sol (L252-263)
```text
    function _sendEthToDepositPool(uint256 _amount) internal {
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ethValueInWithdrawal > _amount) {
            ethValueInWithdrawal -= _amount;
        } else {
            ethValueInWithdrawal = 0;
        }
        // Send eth to deposit pool
        ILRTDepositPool(lrtDepositPoolAddress).receiveFromLRTConverter{ value: _amount }();
        emit EthTransferred(lrtDepositPoolAddress, _amount);
    }
```

**File:** contracts/LRTDepositPool.sol (L498-499)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```
