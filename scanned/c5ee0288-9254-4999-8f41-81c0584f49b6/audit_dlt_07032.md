# [M] Multiple initialization in `NoteInterest`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-canto-v2
Published: 2022-06-29
Source: https://github.com/code-423n4/2022-06-canto-v2-findings/issues/49
Type: code-finding

## Details
# Lines of code

https://github.com/Plex-Engineer/lending-market-v2/blob/2646a7676b721db8a7754bf5503dcd712eab2f8a/contracts/NoteInterest.sol#L99


# Vulnerability details

## Impact
The `initialize` method of the contract `NoteInterest` can be initialized multiple times.

## Proof of Concept

The method `initialize` of the contract `NoteInterest` looks like this:

```javascript
    function initialize(address cnoteAddr, address oracleAddress) external {
        if (msg.sender != admin ) {
            revert SenderNotAdmin(msg.sender);
        }   
        address oldPriceOracle = address(oracle);
        cNote = CErc20(cnoteAddr);
        oracle = PriceOracle(oracleAddress);
        emit NewPriceOracle(oldPriceOracle, oracleAddress);
    }
```

Nothing prevents it from being initialized again and altering the initial values of the contract. This allows the government, unnecessarily, to be able to perform attacks such as altering the logic of the `updateBaseRate` method.

## Recommended Mitigation Steps
- And a require to check that was not already initialized.
