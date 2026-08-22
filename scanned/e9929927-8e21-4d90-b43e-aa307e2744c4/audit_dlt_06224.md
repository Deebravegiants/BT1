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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/28_
