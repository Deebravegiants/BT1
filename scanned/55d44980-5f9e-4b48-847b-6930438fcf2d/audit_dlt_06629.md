# [H] User can reset the INDEFINITE_FUTURE mintTime

## Summary
Severity: High
Chain: Smart contract
Component: Circles
Published: 2024-09-05
Source: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/1
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x656ba747c9cf205046fac382c4ea7acfdf437e1261a20107b208517353de9e74
**Severity:** high

**Description:**
The `stop` function is designed to prevent any future mints by setting `lastMintTime` to `INDEFINITE_FUTURE`. This action is intended to be irreversible.

```javascript
    function stop() external {
        if (!isHuman(msg.sender)) {
            // Only human can call stop.
            revert CirclesHubMustBeHuman(msg.sender, 2);
        }
        MintTime storage mintTime = mintTimes[msg.sender];
        // check if already stopped
=>        if (mintTime.lastMintTime == INDEFINITE_FUTURE) {
            return;
        }
        // stop future mints of personal Circles
        // by setting the last mint time to indefinite future.
        mintTime.lastMintTime = INDEFINITE_FUTURE;

        emit Stopped(msg.sender);
    }

```
The issue, however, is that a user can reset the `mintTime.lastMintTime` after it has been set to `INDEFINITE_FUTURE`, which violates a key aspect of the protocol: once the `stop` function is executed, it should be irreversible.

The user can do so simply by calling `calculateIssuanceWithCheck`:
```javascript
    function calculateIssuanceWithCheck(address _human) external returns (uint256, uint256, uint256) {
        // check if v1 Circles is known to be stopped and update status
        _checkHumanV1CirclesStatus(_human);
        // calculate issuance for the human avatar, but don't mint
        return _calculateIssuance(_human);
    }
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/1_
