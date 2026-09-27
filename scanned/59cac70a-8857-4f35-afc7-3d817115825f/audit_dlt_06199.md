# [M] 2300 gas unit-fixed is not enough for sending Native ETH from the EtherFiNode contract to the Treasury contract via the EtherFiNode#`withdrawFunds()`

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-15
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/54
Type: hats-finding

## Details
**Github username:** @0xmuxyz
**Twitter username:** --
**Submission hash (on-chain):** 0x834c2aefee1a5e8b690e5084d0503016ac1a4cf4d2fa334bb94c4a7eaa27ab4d
**Severity:** medium

**Description:**
## Description
When a full withdrawal, the EtherFiNodesManager#`fullWithdraw()` would be called.

Within the EtherFiNodesManager#`fullWithdraw()`, the EtherFiNodesManager#`_distributePayouts()` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L259
```solidity
    /// @notice process the full withdrawal
    /// @dev This fullWithdrawal is allowed only after it's marked as EXITED.
    /// @dev EtherFi will be monitoring the status of the validator nodes and mark them EXITED if they do;
    /// @dev It is a point of centralization in Phase 1
    /// @param _validatorId the validator Id to withdraw from
    function fullWithdraw(uint256 _validatorId) public nonReentrant whenNotPaused{
        ...
        _distributePayouts(_validatorId, toTreasury, toOperator, toTnft, toBnft); ///<------------------ @audit
        ...
```

When a partial withdrawal to skim rewards, the EtherFiNodesManager#`partialWithdraw()` would be called.

Within the EtherFiNodesManager#`partialWithdraw()`, the EtherFiNodesManager#`_distributePayouts()` would be called as well like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L229
```solidity
    /// @notice Process the rewards skimming
    /// @param _validatorId The validator Id
    function partialWithdraw(uint256 _validatorId) public nonReentrant whenNotPaused {
        ...
        _distributePayouts(_validatorId, toTreasury, toOperator, toTnft, toBnft); ///<------------------ @audit
    }
```

Within the EtherFiNodesManager#`_distributePayouts()`, the EtherFiNode#`withdrawFunds()` would be called like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNodesManager.sol#L495-L500
```solidity
    function _distributePayouts(uint256 _validatorId, uint256 _toTreasury, uint256 _toOperator, uint256 _toTnft, uint256 _toBnft) internal {
        address etherfiNode = etherfiNodeAddress[_validatorId];
        IEtherFiNode(etherfiNode).withdrawFunds( ///<------------------ @audit
            treasuryContract, _toTreasury,
            auctionManager.getBidOwner(_validatorId), _toOperator,
            tnft.ownerOf(_validatorId), _toTnft,
            bnft.ownerOf(_validatorId), _toBnft
        );
    }
```

Within the EtherFiNode#`withdrawFunds()`, funds (Native ETH) would be transferred from this EtherFiNode (Withdrawal Safe) contract to the 4 associated parties (bNFT, tNFT, treasury, nodeOperator) like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNode.sol#L163-L169
```solidity
    /// @dev transfer funds from the withdrawal safe to the 4 associated parties (bNFT, tNFT, treasury, nodeOperator)
    function withdrawFunds(
        address _treasury,
        uint256 _treasuryAmount,
        address _operator,
        uint256 _operatorAmount,
        address _tnftHolder,
        uint256 _tnftAmount,
        address _bnftHolder,
        uint256 _bnftAmount
    ) external onlyEtherFiNodeManagerContract {

        // the recipients of the funds must be able to receive the fund
        // For example, if it is a smart contract, 
        // they should implement either receive() or fallback() properly
        // It's designed to prevent malicious actors from pausing the withdrawals
        bool sent;
        (sent, ) = payable(_operator).call{value: _operatorAmount, gas: 10000}("");  ///<------------- @audit
        _treasuryAmount += (!sent) ? _operatorAmount : 0;
        (sent, ) = payable(_bnftHolder).call{value: _bnftAmount, gas: 10000}("");  ///<------------- @audit
        _treasuryAmount += (!sent) ? _bnftAmount : 0; 
        (sent, ) = payable(_tnftHolder).call{value: _tnftAmount, gas: 12000}(""); // to support 'receive' of LP  ///<------------- @audit
        _treasuryAmount += (!sent) ? _tnftAmount : 0;
        (sent, ) = _treasury.call{value: _treasuryAmount, gas: 2300}(""); ///<------------- @audit
        require(sent, "Failed to send Ether");
    }
```

However, within the EtherFiNode#`withdrawFunds()` above, the `_treasuryAmount` of Native ETH would be transferred to the Treasury contract (`_treasury`) with the **small** and **fixed** amount of gas unit (`2300` gas) like this: \
https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNode.sol#L169
```solidity
(sent, ) = _treasury.call{value: _treasuryAmount, gas: 2300}("")
```
This is problematic. Because both the sender (the [EtherFiNode contract](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/EtherFiNode.sol#L11)) and the receiver (the [Treasury contract](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/Treasury.sol#L8)) would be a smart contract respectively. In this case, the **2300 gas limit** might not be enough for smart contract interactions. 
For example, if the receiver contract has a `receive()` function or `fallback()` function that takes more than **2300 gas units**, which is too low. (Remarks: The [`receive()` function would be implemented in the Treasury contract](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/Treasury.sol#L26)) \
In another scenario, if a congestion would occur on Ethereum Mainnet, a transaction cost would be higher than a usual. In this case, 2300 gas units cause an insufficient gas to send Native ETH.

This lead to reverting to transfer funds (Native ETH) from the EtherFiNode contract to the Treasury contract via the EtherFiNode#`withdrawFunds()` when a full withdrawal or a partial withdrawal.

> **Note**
> This is one of known-issue. Below are a similar findings in the past reports, which were confirmed as a medium severity. And therefore, I marked this vulnerability as a medium severity.  
> - https://solodit.xyz/issues/m-01-operator-might-be-unable-to-withdraw-rewards-due-to-gas-limit-pashov-none-smoothly-markdown
> 
> - https://github.com/sherlock-audit/2023-03-sense-judging/issues/33 (NOTE：In this reports, the `transfer()` method would be used instead of a low-level-call. But, the root cause that **2300 gas unit** is too small to send ETH for interacting smart contracts would be same)


## Impact
This lead to reverting to transfer funds (Native ETH) from the EtherFiNode contract to the Treasury contract via the EtherFiNode#`withdrawFunds()` when a full withdrawal or a partial withdrawal.


## Recommendation
Within the EtherFiNode#`withdrawFunds()`, consider removing the **fixed-gas limit (`2300`)** from the low-level call that send Native ETH to the Treasury contract like this: 
```diff
    /// @dev transfer funds from the withdrawal safe to the 4 associated parties (bNFT, tNFT, treasury, nodeOperator)
    function withdrawFunds(
        address _treasury,
        uint256 _treasuryAmount,
        address _operator,
        uint256 _operatorAmount,
        address _tnftHolder,
        uint256 _tnftAmount,
        address _bnftHolder,
        uint256 _bnftAmount
    ) external onlyEtherFiNodeManagerContract {

        // the recipients of the funds must be able to receive the fund
        // For example, if it is a smart contract, 
        // they should implement either receive() or fallback() properly
        // It's designed to prevent malicious actors from pausing the withdrawals
        bool sent;
        (sent, ) = payable(_operator).call{value: _operatorAmount, gas: 10000}("");
        _treasuryAmount += (!sent) ? _operatorAmount : 0;
        (sent, ) = payable(_bnftHolder).call{value: _bnftAmount, gas: 10000}("");
        _treasuryAmount += (!sent) ? _bnftAmount : 0;
        (sent, ) = payable(_tnftHolder).call{value: _tnftAmount, gas: 12000}(""); // to support 'receive' of LP
        _treasuryAmount += (!sent) ? _tnftAmount : 0;
+       (sent, ) = _treasury.call{value: _treasuryAmount}(""); 
-       (sent, ) = _treasury.call{value: _treasuryAmount, gas: 2300}("");
        require(sent, "Failed to send Ether");
    }
```
