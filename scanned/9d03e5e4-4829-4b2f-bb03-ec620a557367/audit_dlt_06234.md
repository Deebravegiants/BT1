# [M] Owner can renounce ownership of LoyaltyPointsMarketSafe

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-06
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/18
Type: hats-finding

## Details
**Github username:** @jonsey
**Submission hash (on-chain):** 0x76b847d2dc64f8c3e3ce7c964cc53dc66643c919edad609e72b33d0cac0b9426
**Severity:** medium

**Description:**
**Description**\
`LoyaltyPointsMarketSafe` inherits from Openzeppelin `Ownable` which allows the owner to `renounceOwnership` of the contract.

**Attack Scenario**\
Calling this `renounceOwnership` will leave the contract without an owner, preventing any further administrative operations. Specifically `withdrawFunds` will not be able to be called, locking any depositied funds in the contract. Also `setWeiPerPoint` and `setBoostPaymentAmount` will not be callable.  

**Risk level**\
Likelihood - 1
Impact - 5
**Overall: Medium**

**Attachments**

1. **Proof of Concept (PoC) File**
```solidity
  function renounceOwnership() public virtual onlyOwner {
        _transferOwnership(address(0));
    }
```

2. **Revised Code File (Optional)**
It is recommended that the owner should not be able to renounce ownership without transfering the ownership first.  The functionality can be disabled by adding the following code to the `LoyaltyPointsMarketSafe`.

```solidity
function renounceOwnership() public override onlyOwner {
	revert("Cannot renounce ownership");
}
```
