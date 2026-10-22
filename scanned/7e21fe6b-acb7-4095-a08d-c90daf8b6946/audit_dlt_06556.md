# [M] Missing Validation in addSafe Function for Enabled Guard and Module

## Summary
Severity: Medium
Chain: Smart contract
Component: Palmera
Published: 2024-06-26
Source: https://github.com/hats-finance/Palmera-0x5fee7541ddcd51ba9f4af606f87b2c42eea655be/issues/57
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Twitter username:** 0xmahdirostami
**Submission hash (on-chain):** 0x8a527a1f843f29b2f7a4238c2a3b6e9293d5b4b1578f27446bdde2cca03e742b
**Severity:** medium

**Description:**
# Title: Missing Validation in `addSafe` Function for Enabled Guard and Module

**Description**:
The `addSafe` function currently does not validate whether the `msg.sender` has enabled the guard and the `PalmeraModule`. This oversight allows safes to be added to an organization without any guard, leading to potential security issues and possible Denial of Service (DoS) in the `disconnectSafe` and `removeWholeTree` functions.

**Impact:**
- Unauthorized safes can be added to an organization without the necessary guard.
- DoS vulnerabilities in `disconnectSafe` and `removeWholeTree` due to lack of validation.

**Proof of Concept (PoC):**

To demonstrate the issue, make the following changes in `SafeHelper.t.sol`:
```diff
function newPalmeraSafe(uint256 numberOwners, uint256 threshold)
    public
    virtual
    returns (address)
{
    require(
        privateKeyOwners.length >= numberOwners,
        "not enough initialized owners"
    );
    require(
        countUsed + numberOwners <= privateKeyOwners.length,
        "No private keys available"
    );
    require(palmeraModuleAddr != address(0), "Palmera module not set");
    address[] memory owners = new address[](numberOwners);
    for (uint256 i; i < numberOwners; ++i) {
        owners[i] = vm.addr(privateKeyOwners[i + countUsed]);
        countUsed++;
    }
    bytes memory emptyData;
    bytes memory initializer = abi.encodeWithSignature(
        "setup(address[],uint256,address,bytes,address,address,uint256,address)",
        owners,
        threshold,
        address(0x0),
        emptyData,
        address(0x0),
        address(0x0),
        uint256(0),
        payable(address(0x0))
    );

    address safeWalletProxy = safeFactory.newSafeProxy(initializer);
    safeWallet = GnosisSafe(payable(address(safeWalletProxy)));

+    // /// Enable module
+    // bool result = enableModuleTx(address(safeWallet));
+    // require(result == true, "failed enable module");

+    // /// Enable Guard
+    // result = enableGuardTx(address(safeWallet));
+    // require(result == true, "failed enable guard");
    return address(safeWallet);
}
```
This will prevent setting the guard and enabling the module before adding to the safe.

Add the following test to `SkipStressTestStorage`:
```solidity
function testAddSubSafe() public {
    (uint256 rootId, uint256 safeIdA1) =
        palmeraSafeBuilder.setupRootOrgAndOneSafe(orgName, safeA1Name);
    address safeBaddr = safeHelper.newPalmeraSafe(4, 2);
    vm.startPrank(safeBaddr);
    uint256 safeIdB = palmeraModule.addSafe(safeIdA1, safeBName);
    assertEq(palmeraModule.isTreeMember(rootId, safeIdA1), true);
    assertEq(palmeraModule.isSuperSafe(rootId, safeIdA1), true);
    assertEq(palmeraModule.isTreeMember(safeIdA1, safeIdB), true);
    assertEq(palmeraModule.isSuperSafe(safeIdA1, safeIdB), true);
    vm.stopPrank();
}
```

Logs:
```
Suite result: ok. 1 passed; 0 failed; 0 skipped; finished in 43.99ms (11.09ms CPU time)
```
As the logs show, a safe without an enabled guard and module was added successfully.

**Mitigation:**

To mitigate this issue, add a validation check in the `addSafe` function to ensure that the `msg.sender` has enabled the guard and the module before proceeding:


NOTE: This issue exists in other functions as well.
