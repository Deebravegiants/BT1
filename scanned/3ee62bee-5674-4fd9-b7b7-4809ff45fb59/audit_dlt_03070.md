# [M] `emitForWeek` will lose `emissionForWeek` if one week is skipped

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1218
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L207-L208


# Vulnerability details

`emitForWeek` has a mechanism to bring over unclaimed emissions from the previous week:
https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/TapOFT.sol#L207-L208

```solidity
uint256 unclaimed = emissionForWeek[week - 1] - mintedInWeek[week - 1];
uint256 emission = uint256(_computeEmission());
```
`emitForWeek` is `pausable`, meaning that a week may be skipped.

In that case, the unclaimedEmissions from the previous week, would result in a zero.

That would cause the previous emissions to no longer being claimable

### POC

The POC is coded with Foundry and compares the result of skipping a week vs claiming 0 on that week

#### Skipping a Week
```python
[PASS] testSkipAWeek() (gas: 142286)
Logs:
  week1 469157964000000000000000
  week2 465029373916800000000000
  week4 465029373916800000000000
```
#### Not Claiming for a week
```python
[PASS] testNoSkip() (gas: 165882)
Logs:
  week1 469157964000000000000000
  week2 465029373916800000000000
  week4 921874230852664320000000
```

```solidity

// SPDX-License Identifier: MIT

pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "forge-std/console2.sol";

contract TapEmitter {
    uint256 public constant INITIAL_SUPPLY = 46_686_595 * 1e18; // Everything minus DSO
    uint256 public dso_supply = 53_313_405 * 1e18;

    /// @notice the a parameter used in the emission function;
    uint256 constant decay_rate = 8800000000000000; // 0.88%
    uint256 constant DECAY_RATE_DECIMAL = 1e18;

    /// @notice seconds in a week
    uint256 public constant WEEK = 604800;

    /// @notice starts time for emissions
    /// @dev initialized in the constructor with block.timestamp
    uint256 public immutable emissionsStartTime;

    /// @notice returns the amount of emitted TAP for a specific week
    /// @dev week is computed using (timestamp - emissionStartTime) / WEEK
    mapping(uint256 => uint256) public emissionForWeek;

    /// @notice returns the amount minted for a specific week
    /// @dev week is computed using (timestamp - emissionStartTime) / WEEK
    mapping(uint256 => uint256) public mintedInWeek;

    /// @notice returns the minter address
    address public minter;

    /// @notice LayerZero governance chain identifier
    uint256 public governanceChainIdentifier;

    /// @notice returns the pause state of the contract
    bool public paused;





    constructor(
    ) {
        emissionsStartTime = block.timestamp;
    }


    function claim(uint256 week, uint256 amt) external {
        mintedInWeek[week] = amt;
    }

    function emitForWeek(uint256 week) external returns (uint256) {
        /// @audit replaced mintedInWeek[week - 1] with claimed for simplicity

        if (emissionForWeek[week] > 0) return 0;

        // Update DSO supply from last minted emissions
        dso_supply -= mintedInWeek[week - 1]; // NOTE: If no claims then more tokens can be minted since the decay is applied to a bigger number

        // Compute unclaimed emission from last week and add it to the current week emission
        uint256 unclaimed = emissionForWeek[week - 1] - mintedInWeek[week - 1];
        uint256 emission = uint256(_computeEmission()); // TODO: see influence
        emission += unclaimed;
        emissionForWeek[week] = emission;

        return emission;
    }

    function _computeEmission() internal view returns (uint256 result) {
        result = (dso_supply * decay_rate) / DECAY_RATE_DECIMAL;
    }
}

contract CompoundedStakesFuzz is Test {
    TapEmitter e;
    function setUp() public {
        e = new TapEmitter();
    }
    
    function testSkipAWeek() public {
        uint256 week = 1;
        uint256 week1 = e.emitForWeek(week);
        console2.log("week1", week1);
        e.claim(week, week1);


        week++;

        uint256 week2 = e.emitForWeek(week);
        console2.log("week2", week2);
        e.claim(week, week2);

        
        week++;
        week++; // Skip a week

        uint256 week4 = e.emitForWeek(week);
        console2.log("week4", week4);
    }

    function testNoSkip() public {
        uint256 week = 1;
        uint256 week1 = e.emitForWeek(week);
        console2.log("week1", week1);
        e.claim(week, week1);


        week++;

        uint256 week2 = e.emitForWeek(week);
        console2.log("week2", week2);
        e.claim(week, week2);

        
        week++;
        uint256 week3 = e.emitForWeek(week);
        e.claim(week, 0); // Should be equivalent

        week++; // Skip a week

        uint256 week4 = e.emitForWeek(week);
        console2.log("week4", week4);
    }
}

```

### Mitigation

Consider removing the pause from emissions to ensure they happen reliably

If you wish to prevent claiming during pauses, you can keep a pause on `extractTAP`


## Assessed type

Governance
