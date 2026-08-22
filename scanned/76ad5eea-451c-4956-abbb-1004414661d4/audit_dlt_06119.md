# [?] AURA claims on withdraw, HarvestedReward(stakingContract) is not emitted (low severity)

## Summary
Severity: Unknown
Chain: Smart contract
Component: VMEX
Published: 2023-07-25
Source: https://github.com/hats-finance/VMEX-0xb6861bdeb368a1bf628fc36a36cec62d04fb6a77/issues/3
Type: hats-finding

## Details
**Communication channel:** GalloDaSballo (discord)

https://github.com/VMEX-finance/vmex/blob/790ed430e45874e66f6ce461457d1e511561590d/packages/contracts/contracts/protocol/incentives/ExternalRewardDistributor.sol#L119-L120

```solidity
      emit HarvestedReward(stakingContract);

```

Is not emitted but withdrawing from AURA claims rewards

**Attack Scenario**\

The event is emitted on Harvest, however, Aura Withdrawals have the `claim` parameter set to `true` this means those rewards will be harvested without triggering an event

**POC**
```solidity
      require(IAuraRewardPool(stakingContract).withdrawAndUnwrap(amount, true), "aura unstaking failed");

```

As yo can see
```solidity
    function withdrawAndUnwrap(uint256 amount, bool claim) public returns(bool){
        _withdrawAndUnwrapTo(amount, msg.sender, msg.sender);
        //get rewards too
        if(claim){
            getReward(msg.sender,true);
        }
        return true;
    }
```
https://optimistic.etherscan.io/address/0x9f43f726df654e033b04c39989af90ab44875feb#code#F14#L260

Will trigger a claim
##
