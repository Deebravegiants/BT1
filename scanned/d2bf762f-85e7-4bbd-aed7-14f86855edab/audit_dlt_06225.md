# [M] Anyone can bypass the whitelist in `RegulationsManager`, even after the owner removed them

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/27
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xec9763f50c77dc5fdde4f186f71c388cf0b05e127b92ff39f2397b173006dbfe
**Severity:** medium

**Description:**
## Impact
Blacklisted users can whitelist themselves and interact with the contracts 

## Description
Anyone can set themselves as whitelisted or eligible by getting the `correctVersionHash` with `whitelistVersion` from the contract and calling `confirmEligibility()`, even though they might be ineligible due to being from a blacklisted country or other reasons.

 `src/RegulationsManager.sol` - [`confirmEligibility()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/RegulationsManager.sol#L51-L57)
 
 ```solidity
     /// @notice sets a user apart of the whitelist, confirming they are not in a blacklisted country
     function confirmEligibility(bytes32 _hash) external whenNotPaused { // @audit m - anyone can set themselves as eligible
        require(correctVersionHash[whitelistVersion] == _hash, "Incorrect hash");
        isEligible[whitelistVersion][msg.sender] = true;
        declarationHashes[msg.sender] = keccak256(abi.encodePacked(_hash, msg.sender));

        emit EligibilityConfirmed(whitelistVersion, _hash, msg.sender);
    }

 ```
 
The problem is that even though an owner removed the account from the whitelist, the blacklisted user can still make their account whitelisted and reset their eligibility to `true` by simply calling `confirmEligiblity()` after the removal. There is no access control in place that would prevent this.

## Proof of Concept
1. navigate to `test/RegulationsManager.t.sol`
2. copy the below proof of concept inside `RegulationManagerTest` contract
3. run `forge test --match-test test_WhitelistBypass_0xfuje`
```solidity
    function test_WhitelistBypass_0xfuje() public {
        uint32 version = regulationsManagerInstance.whitelistVersion();
        bytes32 hash = regulationsManagerInstance.correctVersionHash(version);

        // bob whitelist himself even though he is from a regulated country
        vm.prank(bob);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/27_
