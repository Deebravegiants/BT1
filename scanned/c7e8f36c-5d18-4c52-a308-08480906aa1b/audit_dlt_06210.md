# [M] Possible to grief and prevent protocol from migration in `NodeOperatorManager.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-10
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/42
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xcdf04182447950f2a421c34e08da524cc18f04953d78c3e7349310e282306659
**Severity:** medium

**Description:**
## Impact
Protocol can lose huge gas fees, temporary prevention of migration until the issue is fixed

## Description
The `initializeOnUpgrade()` in `NodeOperatorManager` registers every operator with their `totalKeys`, `keysUsed` and `ipfsHash`: this might be a quite expensive operation depending on how much operators need to be migrated. An attacker can prevent the migration and grief the protocol with gas fees during the process.

`src/NodeOperatorManager.sol` - [`initializeOnUpgrade()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/NodeOperatorManager.sol#L57-L83)
```solidity
    /// @notice Migrates operator details from previous contract
    /// @dev Our previous node operator contract was non upgradeable. We will be moving to an upgradeable version but need this
    ///         function to migrate the data
    function initializeOnUpgrade(
        address[] memory _operator, 
        bytes[] memory _ipfsHash,
        uint64[] memory _totalKeys,
        uint64[] memory _keysUsed
    ) external onlyOwner {
        require((_operator.length == _ipfsHash.length) && (_operator.length == _totalKeys.length) && (_operator.length == _keysUsed.length), "Invalid lengths");
        for(uint256 x = 0; x < _operator.length; x++) {
            require(!registered[_operator[x]], "Already registered");

            KeyData memory keyData = KeyData({
                totalKeys: _totalKeys[x],
                keysUsed: _keysUsed[x],
                ipfsHash: abi.encodePacked(_ipfsHash[x])
            });

            addressToOperatorData[_operator[x]] = keyData;
            registered[_operator[x]] = true;

            emit OperatorRegistered(
                _operator[x],
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/42_
