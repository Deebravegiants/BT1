# [M] Incorrect time check in `src/modules/paymentProcessor/PP_Streaming_v1.sol::validTimes`

## Summary
Severity: Medium
Chain: Smart contract
Component: Inverter-Network
Published: 2024-06-07
Source: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/53
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0xf4000c5b639a2c99048a903915028e8df1ff5dbc0ed39d54659158a37d4c5c50
**Severity:** medium

**Description:**
**Description**\

The time validation check is incorrectly implemented in `src/modules/paymentProcessor/PP_Streaming_v1.sol::validTimes`.

In `src/modules/paymentProcessor/PP_Streaming_v1.sol::validTimes`:
```javascript
/// @notice validate uint start input.
    /// @param _start uint to validate.
    /// @param _cliff uint to validate.
    /// @param _end uint to validate.
    /// @return True if uint is valid.
    function validTimes(uint _start, uint _cliff, uint _end)
        internal
        pure
        returns (bool)
    {
        return !(_start >= type(uint).max && _start + _cliff > _end);
    }
```

In this function, `||` should be used instead of `&&` operator. As a result, invalid times will be treated as valid.

**Attack Scenario**\

Invalid times being treated as valid, this will put protocol in an unexpected state.


**Attachments**

NA

1. **Proof of Concept (PoC) File**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Inverter-Network-0xe47e52c4fea05e555920f1dcdcc6fb8eca103eeb/issues/53_
