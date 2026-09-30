# [?] Merge pull request #534 from safe-global/feat/fbhandler-exploit

## Summary
Severity: Unknown
Chain: Safe
Component: safe-fndn/safe-smart-account
Published: 2023-03-21
Source: https://github.com/safe-fndn/safe-smart-account/commit/acea9c53f1905fba32a56f4a8e5870f0c7277dd3
Type: security-commit

## Details
Merge pull request #534 from safe-global/feat/fbhandler-exploit

Check that fallback handler address is not equal to self

## Patch
### contracts/base/FallbackManager.sol
```diff
@@ -18,6 +18,21 @@ abstract contract FallbackManager is SelfAuthorized {
      *  @param handler contract to handle fallback calls.
      */
     function internalSetFallbackHandler(address handler) internal {
+        /*
+            If a fallback handler is set to self, then the following attack vector is opened:
+            Imagine we have a function like this:
+            function withdraw() internal authorized {
+                withdrawalAddress.call.value(address(this).balance)("");
+            }
+
+            If the fallback method is triggered, the fallback handler appends the msg.sender address to the calldata and calls the fallback handler.
+            A potential attacker could call a Safe with the 3 bytes signature of a withdraw function. Since 3 bytes do not create a valid signature,
+            the call would end in a fallback handler. Since it appends the msg.sender address to the calldata, the attacker could craft an address 
+            where the first 3 bytes of the previous calldata + the first byte of the address make up a valid function signature. The subsequent call would result in unsanctioned access to Safe's internal protected methods.
+            For some reason, solidity matches the first 4 bytes of the calldata to a function signature, regardless if more data follow these 4 bytes.
+        */
+        require(handler != address(this), "GS400");
+
         bytes32 slot = FALLBACK_HANDLER_STORAGE_SLOT;
         // solhint-disable-next-line no-inline-assembly
         assembly {
@@ -29,6 +44,7 @@ abstract contract FallbackManager is SelfAuthorized {
      * @notice Set Fallback Handler to `handler` for the Safe.
      * @dev Only fallback calls without value and with data will be forwarded.
      *      This can only be done via a Safe transaction.
+     *      Cannot be set to the Safe itself.
      * @param handler contract to handle fallback calls.
      */
     function setFallbackHandler(address handler) public authorized {
```

### docs/error_codes.md
```diff
@@ -44,3 +44,6 @@
 
 ### Guard management related
 - `GS300`: `Guard does not implement IERC165`
+
+### Fallback handler related
+- `GS400`: `Fallback handler cannot be set to self`
\ No newline at end of file
```

### test/core/Safe.FallbackManager.spec.ts
```diff
@@ -151,5 +151,16 @@ describe("FallbackManager", async () => {
                     "0000000000000000",
             );
         });
+
+        it("cannot be set to self", async () => {
+            const { safe } = await setupWithTemplate();
+            // Setup Safe
+            await safe.setup([user1.address], 1, AddressZero, "0x", AddressZero, AddressZero, 0, AddressZero);
+
+            // The transaction execution function doesn't bubble up revert messages so we check for a generic transaction fail code GS013
+            await expect(executeContractCallWithSigners(safe, safe, "setFallbackHandler", [safe.address], [user1])).to.be.revertedWith(
+                "GS013",
+            );
+        });
     });
 });
```

### test/core/Safe.Setup.spec.ts
```diff
@@ -385,5 +385,13 @@ describe("Safe", async () => {
                 template.setup([user1.address], 1, user2.address, "0xbeef73", AddressZero, AddressZero, 0, AddressZero),
             ).to.be.revertedWith("GS002");
         });
+
+        it("should fail if tried to set the fallback handler address to self", async () => {
+            const { template } = await setupTests();
+
+            await expect(
+                template.setup([user1.address], 1, AddressZero, "0x", template.address, AddressZero, 0, AddressZero),
+            ).to.be.revertedWith("GS400");
+        });
     });
 });
```
