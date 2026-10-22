# [M] Admin Can Always Update lscales Levels

## Summary
Severity: Medium
Contest weight: 0.4137
Dataset id: 15002
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Situation:
An administrator of the protocol can arbitrarily set the lscales levels of users at any moment. This directly impacts the amount that can be collected in the collect() function.
The update of lscales levels can be done by setting the adapter to off, which will allow the require in backfillScale() to continue. Following this, a call to backfillScale() should be done to set arbitrary values to the lscales. Finally, set the adapter back to on.
Although this is protected by requiresTrust, it is probably best to limit this possibility.
```solidity
function setAdapter(address adapter, bool isOn) public requiresTrust {
    _setAdapter(adapter, isOn);
}
function backfillScale(..., address[] calldata _usrs, uint256[] calldata _lscales) external requiresTrust {
    ...
    // continues when adapters[adapter] == false
    require(!adapters[adapter] || block.timestamp > cutoff, ...);
    /* Set user's last scale values the Series (needed for the `collect` method) */
    for (uint256 i = 0; i < _usrs.length; i++) {
        lscales[adapter][maturity][_usrs[i]] = _lscales[i];
    }
    ...
}
```

## Recommendation
Double check the circumstances under which an administrator can perform such updates.
