# [M] Hardcoding block formation time will cause serious effects on `tierPoints` calculations when block formation time changes

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/28
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Submission hash (on-chain):** 0xd943071b0ea374f7753e8a174551d8b1bed2f10436568c176b2819204a234d0e
**Severity:** medium

**Description:**
**Description**\

`MembershipNFT.computeTierPointsForEap()` is used to compute the `tierPoints`for Early Adapter Pool(EAP). This function is extensively used in following contracts,

1) `MembershipManager.computeTierPointsForEap()` which can be checked [here](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L124)

2) `MembershipManagerV0.wrapEthForEap()` which can be checked [here](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManagerV0.sol#L125)

3) `MembershipManagerV0.recoverTierPointsForEap()` which can be checked [here](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManagerV0.sol#L349)


All these function takes argument `_eapDepositBlockNumber` per the `computeTierPointsForEap()` function, This can be checked below(*kept relevant code for simpler issue understanding*)

```Solidity
File: src/MembershipNFT.so

    function computeTierPointsForEap(uint32 _eapDepositBlockNumber) public view returns (uint40) {


        // some code


        // They kept staking with us after the EAP ended
        // One tier point per hour
        // While the actual block generation time is slightly larger than 12 seconds
        // we use 13 seconds to compenstae our users pain during the days after the EAP
        tierPoints += (13 * (uint40(block.number) - eapCloseBlockNumber)) / 3600;

        return tierPoints;
    }
```

The issue here is, this function has used **hardcoded block generation time** which is 13 seconds being considered in contract for Ethereum block chain. 

Hardcoding block generation time wont allow to change it if the ethereum block time changes after any future hard forks. The last time it got changed in september, 2022 where the block time got reduced from 15 seconds to 12 seconds. 

Ethereum blockchain has several future upgrades in coming years, some big changes like Ethereum sharding will be the game changer for ethereum as it will allow for its scalability. This major upgrade will reduce the block time further and it is expected it will slash the block formation time by twice.

Consider a scenario,

We have, 

```Solidity
uint32 eapCloseBlockNumber = 17664247;
```

For our example scenario, lets find the `tierPoints` to get the issue better,

```Solidity
        tierPoints += (13 * (uint40(block.number) - eapCloseBlockNumber)) / 3600;
```

Current block.number at the time of writing this report is `18521824`

Considering 13 seconds as block time, `tierPoints` will be 3096.

```Solidity
tierPoints += (18521824 - 17664247) * 13 / 3600 
tierPoints +=  857577 * 13/ 3600
tierPoints += 3096
```

However, if we consider the Ethereum future forks which ofcourse going to reduce the block formation period, lets consider 6 seconds in our scenario so the `tierPoints` will be 1429.

```Solidity
tierPoints += (18521824 - 17664247) * 6 / 3600 
tierPoints +=  857577 * 6/ 3600
tierPoints += 1429
```

Now, this is huge effect if the Ethereum block formation period is hardcoded, we have considered 6 seconds even it could be 2 seconds probably by next year the effect on `tierPoints` calculation will be huge.


Function like `MembershipManager.computeTierPointsForEap()`, `MembershipManagerV0.wrapEthForEap()`, `MembershipManagerV0.recoverTierPointsForEap()`

will be severily affected by this issue as if the hardcoded block time is kept, the tierPoints will be calculated more and will be rewarded more which should not be the desired behavior here. tier points have a direct relationship to staking rewards so while calculating the `tierPoints` an extra prevention is required. This issue is very much possible in few months after the Ethereum fork and the issue is identified as Medium severity as it will break the intended functionality wrt to `tierPoints` calculation which is one of the core functionality of protocol.


**Attack Scenario**\
As described above.

**Attachments**

1. **Proof of Concept (PoC) File**

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipNFT.sol#L334


2. **Revised Code File (Optional)**
Block formation time should be changeable and it should not be hardcoded. 

Recommend below high level mitigation to resolve the issue,

```diff
File: src/MembershipNFT.sol

+ // Ethereum block formation period which is being considered as 13 seconds for now
+ uint256 blockTime = 13;

+ // function to change the blockTime if Ethereum changes it after hardforks in future, This function can only be accessed by contract owner.
+    function updateBlockTime(uint256 _blockTime) external onlyOwner {
+        require(_blockTime != 0, "Cannot be zero");
+        blockTime  = _blockTime;
+    }


    function computeTierPointsForEap(uint32 _eapDepositBlockNumber) public view returns (uint40) {
        uint8 numTiers = membershipManager.numberOfTiers();
        uint32[] memory lastBlockNumbers = new uint32[](numTiers);
        uint32 eapCloseBlockNumber = 17664247; // https://etherscan.io/tx/0x1ff2ade678bea8b4e5633841ff21390283e57bc50fced4dea54b11ebc929b10c
        
        lastBlockNumbers[0] = 0;
        lastBlockNumbers[1] = eapCloseBlockNumber;
        lastBlockNumbers[2] = 16970393; // https://etherscan.io/tx/0x65bc8e0e5c038fc1569c3b7d9663438696a1e261451a6a57d44373266eda5a19
        lastBlockNumbers[3] = 16755015; // https://etherscan.io/tx/0xe579a56c6c1b1878b368836b682b8fa7c39fe54d6f07750158b570844597e5b4
        
        uint8 tierId;
        if (_eapDepositBlockNumber <= lastBlockNumbers[3]) {
            tierId = 3; // PLATINUM
        } else if (_eapDepositBlockNumber <= lastBlockNumbers[2]) {
            tierId = 2; // GOLD
        } else if (_eapDepositBlockNumber <= lastBlockNumbers[1]) {
            tierId = 1; // SILVER
        } else {
            tierId = 0; // BRONZE
        }
        uint8 nextTierId = (tierId < numTiers - 1) ? tierId + 1 : tierId;

        (,uint40 current,, ) = membershipManager.tierData(tierId);
        (,uint40 next,, ) = membershipManager.tierData(nextTierId);

        // Minimum tierPoints for the current tier
        uint40 tierPoints = current;

        // Linear projection of TierPoints within the tier
        // so that the days in EAP is taken into account for the days remaining for the next tier
        if (tierId != nextTierId) {
            tierPoints += (next - current) * (lastBlockNumbers[tierId] - _eapDepositBlockNumber) / (lastBlockNumbers[tierId] - lastBlockNumbers[nextTierId]);
        }

        // They kept staking with us after the EAP ended
        // One tier point per hour
        // While the actual block generation time is slightly larger than 12 seconds
        // we use 13 seconds to compenstae our users pain during the days after the EAP
-        tierPoints += (13 * (uint40(block.number) - eapCloseBlockNumber)) / 3600;

+        tierPoints += (blockTime  * (uint40(block.number) - eapCloseBlockNumber)) / 3600;

        return tierPoints;
    }
```
