# [?] Merge pull request from GHSA-93hq-5wgc-jc82

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2023-04-13
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/8d633cb7d169f2f8595b273660b00b69e845c2fe
Type: security-commit

## Details
Merge pull request from GHSA-93hq-5wgc-jc82

Co-authored-by: Francisco <fg@frang.io>

## Patch
### .changeset/silent-pugs-scream.md
```diff
@@ -0,0 +1,5 @@
+---
+'openzeppelin-solidity': patch
+---
+
+`GovernorCompatibilityBravo`: Fix encoding of proposal data when signatures are missing.
```

### contracts/governance/compatibility/GovernorCompatibilityBravo.sol
```diff
@@ -70,6 +70,7 @@ abstract contract GovernorCompatibilityBravo is IGovernorTimelock, IGovernorComp
         bytes[] memory calldatas,
         string memory description
     ) public virtual override returns (uint256) {
+        require(signatures.length == calldatas.length, "GovernorBravo: invalid signatures length");
         // Stores the full proposal and fallback to the public (possibly overridden) propose. The fallback is done
         // after the full proposal is stored, so the store operation included in the fallback will be skipped. Here we
         // call `propose` and not `super.propose` to make sure if a child contract override `propose`, whatever code
@@ -149,8 +150,7 @@ abstract contract GovernorCompatibilityBravo is IGovernorTimelock, IGovernorComp
         bytes[] memory calldatas
     ) private pure returns (bytes[] memory) {
         bytes[] memory fullcalldatas = new bytes[](calldatas.length);
-
-        for (uint256 i = 0; i < signatures.length; ++i) {
+        for (uint256 i = 0; i < fullcalldatas.length; ++i) {
             fullcalldatas[i] = bytes(signatures[i]).length == 0
                 ? calldatas[i]
                 : abi.encodePacked(bytes4(keccak256(bytes(signatures[i]))), calldatas[i]);
```

### test/governance/compatibility/GovernorCompatibilityBravo.test.js
```diff
@@ -224,6 +224,21 @@ contract('GovernorCompatibilityBravo', function (accounts) {
         });
       });
 
+      it('with inconsistent array size for selector and arguments', async function () {
+        const target = this.receiver.address;
+        this.helper.setProposal(
+          {
+            targets: [target, target],
+            values: [0, 0],
+            signatures: ['mockFunction()'], // One signature
+            data: ['0x', this.receiver.contract.methods.mockFunctionWithArgs(17, 42).encodeABI()], // Two data entries
+          },
+          '<proposal description>',
+        );
+
+        await expectRevert(this.helper.propose({ from: proposer }), 'GovernorBravo: invalid signatures length');
+      });
+
       describe('should revert', function () {
         describe('on propose', function () {
           it('if proposal does not meet proposalThreshold', async function () {
```
