# [M] `setDelta64x64()` and `setDelta64x64Offset()` does not allow for setting of negative delta value.

## Summary
Severity: Medium
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L64-L93
Type: audit-issue

## Details
# `setDelta64x64()` and `setDelta64x64Offset()` does not allow for setting of negative delta value.

## Summary
Since Knox Finance supports both call and put options, delta value allowed should be in the range (-1,1). 

## Vulnerability Detail

Value of `newDelta64x64` and `newDeltaOffset64x64` is restricted in the range (0,1) when it should be (-1,1).

## Impact
Delta value of < 0 cannot be set which prevents the protocol from supporting put options.

## Code Snippet

[VaultAdmin.sol#L64-L93](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L64-L93)
```solidity
    function setDelta64x64(int128 newDelta64x64) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newDelta64x64 > 0, "delta <= 0");
        require(newDelta64x64 < ONE_64x64, "delta > 1");

        emit DeltaSet(l.epoch, l.delta64x64, newDelta64x64, msg.sender);

        l.delta64x64 = newDelta64x64;
    }
```
```solidity
    function setDeltaOffset64x64(int128 newDeltaOffset64x64)
        external
        onlyOwner
    {
        VaultStorage.Layout storage l = VaultStorage.layout();
        require(newDeltaOffset64x64 > 0, "delta <= 0");
        require(newDeltaOffset64x64 < ONE_64x64, "delta > 1");

        emit DeltaSet(
            l.epoch,
            l.deltaOffset64x64,
            newDeltaOffset64x64,
            msg.sender
        );

        l.deltaOffset64x64 = newDeltaOffset64x64;
    }
```

## Tool used

Manual Review

## Recommendation

```diff
function setDelta64x64(int128 newDelta64x64) external onlyOwner {
        VaultStorage.Layout storage l = VaultStorage.layout();
-       require(newDelta64x64 > 0, "delta <= 0");
+       require(newDelta64x64 > -1, "delta <= -1");
        require(newDelta64x64 < ONE_64x64, "delta > 1");

        emit DeltaSet(l.epoch, l.delta64x64, newDelta64x64, msg.sender);

        l.delta64x64 = newDelta64x64;
}
```
```diff
function setDeltaOffset64x64(int128 newDeltaOffset64x64)
        external
        onlyOwner
    {
        VaultStorage.Layout storage l = VaultStorage.layout();
-        require(newDeltaOffset64x64 > 0, "delta <= 0");
+        require(newDeltaOffset64x64 > -1, "delta <= -1");
         require(newDeltaOffset64x64 < ONE_64x64, "delta > 1");

        emit DeltaSet(
            l.epoch,
            l.deltaOffset64x64,
            newDeltaOffset64x64,
            msg.sender
        );

        l.deltaOffset64x64 = newDeltaOffset64x64;
}
```
