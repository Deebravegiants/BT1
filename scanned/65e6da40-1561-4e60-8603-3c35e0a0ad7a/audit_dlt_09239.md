# [?] Fix ERC777 potential reentrancy issues (#2483)

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2021-01-26
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/3b4c951838ddf82f4d2b44ae7c967f0573039f28
Type: security-commit

## Details
Fix ERC777 potential reentrancy issues (#2483)

## Patch
### CHANGELOG.md
```diff
@@ -15,6 +15,12 @@
  * `EnumerableMap`: fix a memory allocation issue by adding new `EnumerableMap.tryGet(uint)→(bool,address)` functions. `EnumerableMap.get(uint)→string` is now deprecated. ([#2462](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2462))
  * `ERC165Checker`: added batch `getSupportedInterfaces`. ([#2469](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2469))
 
+### Security Fixes
+
+ * `ERC777`: fix potential reentrancy issues for custom extensions to `ERC777`. ([#2483](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2483))
+
+If you're using our implementation of ERC777 from version 3.3.0 or earlier, and you define a custom `_beforeTokenTransfer` function that writes to a storage variable, you may be vulnerable to a reentrancy attack. If you're affected and would like assistance please write to security@openzeppelin.com. [Read more in the pull request.](https://github.com/OpenZeppelin/openzeppelin-contracts/pull/2483)
+
 ## 3.3.0 (2020-11-26)
 
  * Now supports both Solidity 0.6 and 0.7. Compiling with solc 0.7 will result in warnings. Install the `solc-0.7` tag to compile without warnings.
```

### contracts/mocks/ERC777Mock.sol
```diff
@@ -6,6 +6,8 @@ import "../utils/Context.sol";
 import "../token/ERC777/ERC777.sol";
 
 contract ERC777Mock is Context, ERC777 {
+    event BeforeTokenTransfer();
+
     constructor(
         address initialHolder,
         uint256 initialBalance,
@@ -28,4 +30,8 @@ contract ERC777Mock is Context, ERC777 {
     function approveInternal(address holder, address spender, uint256 value) public {
         _approve(holder, spender, value);
     }
+
+    function _beforeTokenTransfer(address, address, address, uint256) internal override {
+        emit BeforeTokenTransfer();
+    }
 }
```

### contracts/mocks/ERC777SenderRecipientMock.sol
```diff
@@ -34,6 +34,9 @@ contract ERC777SenderRecipientMock is Context, IERC777Sender, IERC777Recipient,
         uint256 toBalance
     );
 
+    // Emitted in ERC777Mock. Here for easier decoding
+    event BeforeTokenTransfer();
+
     bool private _shouldRevertSend;
     bool private _shouldRevertReceive;
 
```

### contracts/token/ERC777/ERC777.sol
```diff
@@ -390,10 +390,10 @@ contract ERC777 is Context, IERC777, IERC20 {
 
         address operator = _msgSender();
 
-        _beforeTokenTransfer(operator, from, address(0), amount);
-
         _callTokensToSend(operator, from, address(0), amount, data, operatorData);
 
+        _beforeTokenTransfer(operator, from, address(0), amount);
+
         // Update state variables
         _balances[from] = _balances[from].sub(amount, "ERC777: burn amount exceeds balance");
         _totalSupply = _totalSupply.sub(amount);
```

### test/token/ERC777/ERC777.test.js
```diff
@@ -447,4 +447,37 @@ contract('ERC777', function (accounts) {
       expect(await this.token.defaultOperators()).to.deep.equal([]);
     });
   });
+
+  describe('relative order of hooks', function () {
+    beforeEach(async function () {
+      await singletons.ERC1820Registry(registryFunder);
+      this.sender = await ERC777SenderRecipientMock.new();
+      await this.sender.registerRecipient(this.sender.address);
+      await this.sender.registerSender(this.sender.address);
+      this.token = await ERC777.new(holder, initialSupply, name, symbol, []);
+      await this.token.send(this.sender.address, 1, '0x', { from: holder });
+    });
+
+    it('send', async function () {
+      const { receipt } = await this.sender.send(this.token.address, anyone, 1, '0x');
+
+      const internalBeforeHook = receipt.logs.findIndex(l => l.event === 'BeforeTokenTransfer');
+      expect(internalBeforeHook).to.be.gte(0);
+      const externalSendHook = receipt.logs.findIndex(l => l.event === 'TokensToSendCalled');
+      expect(externalSendHook).to.be.gte(0);
+
+      expect(externalSendHook).to.be.lt(internalBeforeHook);
+    });
+
+    it('burn', async function () {
+      const { receipt } = await this.sender.burn(this.token.address, 1, '0x');
+
+      const internalBeforeHook = receipt.logs.findIndex(l => l.event === 'BeforeTokenTransfer');
+      expect(internalBeforeHook).to.be.gte(0);
+      const externalSendHook = receipt.logs.findIndex(l => l.event === 'TokensToSendCalled');
+      expect(externalSendHook).to.be.gte(0);
+
+      expect(externalSendHook).to.be.lt(internalBeforeHook);
+    });
+  });
 });
```
