# [M] The value emitted in event `ClaimedProceeds` is wrong

## Summary
Severity: Medium
Reporter: ret2basic.eth
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178
Type: audit-issue

## Details
# The value emitted in event `ClaimedProceeds` is wrong

## Summary

In `MeritDutchAuction.claimProceeds()`, event `ClaimedProceeds` always emits 0 instead of `address(this).balance`.

## Vulnerability Detail

In `MeritDutchAuction.claimProceeds()`:

```solidity
    function claimProceeds() external onlyOwner {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance);
    }
```

After the low-level call, `address(this).balance` will be 0 if the ETH balance is transferred out correctly. This means `emit ClaimedProceeds(address(this).balance);` will always emit 0 instead of the ETH balance.

## Impact

The off-chain integration connected to the event `ClaimedProceeds` will always get 0 instead of the correct value, hence the future computation based on this value will be wrong.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L178

## Proof of Concept

Deploy the following contract in Remix IDE and pass 1 ETH into it during deployment:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Test {

    event ClaimedProceeds(uint256 amount);

    constructor () payable {}

    function claimProceeds() external  {
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(address(this).balance);
    }
}
```

Call `claimProceeds()` and examine the event emitted:

```json
	{
		"from": "0x358AA13c52544ECCEF6B0ADD0f801012ADAD5eE3",
		"topic": "0x3ed37094ee4bcaccd75f1334344e63fae3496fc37c91c1679d76cd719b6bc337",
		"event": "ClaimedProceeds",
		"args": {
			"0": "0",
			"amount": "0"
		}
	}
```

The `amount` field is 0, which is supposed to be 1e18 wei (the 1 ETH passed in at deployment time).

## Tool used

Manual Review

## Recommendation

Cache `address(this).balance` in a local variable:

```solidity
    function claimProceeds() external onlyOwner {
        uint256 balance = address(this).balance;
        // Send ETH to the owner
        (bool success, ) = payable(msg.sender).call{value: address(this).balance}(bytes(""));
        // Revert if transfer failed
        require(success, "Claim failed");
        // Emit event for offchain integrations
        emit ClaimedProceeds(balance);
    }
```

Also, use Foundry `expectEmit()` to check events in order to prevent similar issues.
