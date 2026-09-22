# [M] Ineffective TWAV Implementation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-nibbl
Published: 2022-06-24
Source: https://github.com/code-423n4/2022-06-nibbl-findings/issues/191
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-nibbl/blob/8c3dbd6adf350f35c58b31723d42117765644110/contracts/Twav/Twav.sol#L11


# Vulnerability details

## Background

The current TWAV implementation consists of an array of 4 observations/valuations called `twavObservations`. Whenever, the new valuation is updated, the new cumulative valuation will be appended to the `twavObservations` array and the oldest observation/valuation will be removed from the `twavObservations` array.

Description of current TWAV implementation can be found at https://github.com/NibblNFT/nibbl-smartcontracts#twavsol

> - Time-weighted average valuation
> - Uses an array of length 4 which stores cumulative valuation and timestamp.
> - TWAV is calculated between the most and least recent observations recorded in the array.
> - TWAV array is updated only when the system is in buyout state. In case of buyout rejection, the array is reset.

[https://github.com/code-423n4/2022-06-nibbl/blob/8c3dbd6adf350f35c58b31723d42117765644110/contracts/Twav/Twav.sol#L11](https://github.com/code-423n4/2022-06-nibbl/blob/8c3dbd6adf350f35c58b31723d42117765644110/contracts/Twav/Twav.sol#L11)

```solidity
/// @notice current index of twavObservations index
uint8 public twavObservationsIndex;
uint8 private constant TWAV_BLOCK_NUMBERS = 4; //TWAV of last 4 Blocks 
uint32 public lastBlockTimeStamp;

/// @notice record of TWAV 
TwavObservation[TWAV_BLOCK_NUMBERS] public twavObservations;

/// @notice updates twavObservations array
/// @param _blockTimestamp timestamp of the block
/// @param _valuation current valuation
function _updateTWAV(uint256 _valuation, uint32 _blockTimestamp) internal {
    uint32 _timeElapsed; 
    unchecked {
        _timeElapsed = _blockTimestamp - lastBlockTimeStamp;
    }

    uint256 _prevCumulativeValuation = twavObservations[((twavObservationsIndex + TWAV_BLOCK_NUMBERS) - 1) % TWAV_BLOCK_NUMBERS].cumulativeValuation;
    twavObservations[twavObservationsIndex] = TwavObservation(_blockTimestamp, _prevCumulativeValuation + (_valuation * _timeElapsed)); //add the previous observation to make it cumulative
    twavObservationsIndex = (twavObservationsIndex + 1) % TWAV_BLOCK_NUMBERS;
    lastBlockTimeStamp = _blockTimestamp;
}
```

Within the `NibblVault` contract, the `_updateTWAV` function will be called whenever the following events happen during the buyout period:

1. `NibbleVault.buy()` and `NibbleVault.Sell()` functions are called
2. `NibbleVault.initiateBuyout` function is called
3. `NibbleVault.updateTWAV` function is called

Per the code and comment of `_getTwav()` function, the function will return the TWAV of the last four (4) blocks. This function can be called by anyone.

```solidity
/// @notice returns the TWAV of the last 4 blocks
/// @return _twav TWAV of the last 4 blocks
function _getTwav() internal view returns(uint256 _twav){
    if (twavObservations[TWAV_BLOCK_NUMBERS - 1].timestamp != 0) {
        uint8 _index = ((twavObservationsIndex + TWAV_BLOCK_NUMBERS) - 1) % TWAV_BLOCK_NUMBERS;
        TwavObservation memory _twavObservationCurrent = twavObservations[(_index)];
        TwavObservation memory _twavObservationPrev = twavObservations[(_index + 1) % TWAV_BLOCK_NUMBERS];
        _twav = (_twavObservationCurrent.cumulativeValuation - _twavObservationPrev.cumulativeValuation) / (_twavObservationCurrent.timestamp - _twavObservationPrev.timestamp);
    }
}
```

Time weighted average valuation (TWAV) is supposed to be the average value of a security over a specified time (e.g. 15 minutes, 1 hour, 24 hours). However, based on the above implementation of the `_getTwav` function, it is not the average value of a security over a specific time. 

A user could call the `updateTWAV` function to add the new valuation/observation to the `twavObservations` array each time a new Ethereum block is mined. As such, the current implementation becomes the average value of a security over a specific number of observations (in this case 4 observations), thus it can be considered as Observation weighted average valuation (OWAV). 

There is a fundamental difference between TWAV and OWAV.

## Proof-of-Concept

In Ethereum, the average block time is around 15 seconds, so the time to take to mine 4 blocks will be 1 minute. As such, in term of TWAV, the current implementation only have a period of 1 minute, which is too short to prevent price manipulation.

The following shows an example where it is possible to buy tokens→ increase the valuation above the rejection valuation→ reject the buyout→ dump the tokens within 1 minute:

Assume that a buyer has triggered a buyout on the vault/NFT, and the buyout rejection price is 120 ETH and the current valuation is 100 ETH. Further assume that all elements in the  `twavObservations` array have already been populated.

Note: Fees are ignored to illustrate the issue.

1. Block 100 at Time 0 - Attacker called `buy` function to increase the current valuation to 120 ETH attempting to reject the buyout.
2. Block 101 at Time 15 - Attacker called `updateTWAV` function. The current valuation (120 ETH) will be replaced the first element in `twavObservations` array.
3. Block 102 at Time 30 - Attacker called `updateTWAV` function. The current valuation (120 ETH) will be replaced the second element in `twavObservations` array.
4. Block 103 at Time 45 - Attacker called `updateTWAV` function. The current valuation (120 ETH) will be replaced the third element in `twavObservations` array.
5. Block 104 at Time 60 - Attacker called `sell` function to sell/dump all his shares. Within the `sell` function, `_updateTWAV` will be first called, thus the current valuation (120 ETH) will be replaced the fourth element in `twavObservations` array. Then, the `_rejectBuyout()` will be called, and the `_getTwav` function will be triggered. At this point, the TWAV valuation is finally 120 ETH, thus the buyout is rejected. Subseqently, attacker's shares are burned, and attacker get back his funds.

Since attacker could perform the above attack within 1 minute, it is very unlikely that the attackers will lose money to arbitrageurs as it takes some time for the arbitrageurs to notice such an opportunity.

Attacker could also front-run or set a higher gas fee to ensure that their transaction get mined in the next block to minimize the attack window period.

## Impact

Buyout can be easily rejected by attackers

## Recommended Mitigation Steps

Implement a proper TWAV that provides the average value of a security over a specified time. The time period/windows of the TWAV must be explicitly defined (e.g. 15 minutes, 1 hour, 24 hours) in the contract.

There are trade offs when choosing the length of the period of time to calculate a TWAP. Longer periods are better to protect against price manipulation, but come at the expense of a slower, and potentially less accurate, price. Thus, the team should determine the optimal period.

Consider referencing the popular Uniswap V2 TWAP design (https://docs.uniswap.org/protocol/V2/concepts/core-concepts/oracles)
