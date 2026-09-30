# [?] Merge pull request #171 from Recmo/feature/reentrancy-guard

## Summary
Severity: Unknown
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2017-03-28
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/commit/2e9587477c4eb9553bca3fc1b8dfb62b280390f9
Type: security-commit

## Details
Merge pull request #171 from Recmo/feature/reentrancy-guard

Add ReentrancyGuard

## Patch
### contracts/ReentrancyGuard.sol
```diff
@@ -0,0 +1,28 @@
+pragma solidity ^0.4.8;
+
+/// @title Helps contracts guard agains rentrancy attacks.
+/// @author Remco Bloemen <remco@2π.com>
+/// @notice If you mark a function `nonReentrant`, you should also
+/// mark it `external`.
+contract ReentrancyGuard {
+
+  /// @dev We use a single lock for the whole contract.
+  bool private rentrancy_lock = false;
+
+  /// Prevent contract from calling itself, directly or indirectly.
+  /// @notice If you mark a function `nonReentrant`, you should also
+  /// mark it `external`. Calling one nonReentrant function from
+  /// another is not supported. Instead, you can implement a
+  /// `private` function doing the actual work, and a `external`
+  /// wrapper marked as `nonReentrant`.
+  modifier nonReentrant() {
+    if(rentrancy_lock == false) {
+      rentrancy_lock = true;
+      _;
+      rentrancy_lock = false;
+    } else {
+      throw;
+    }
+  }
+
+}
```

### test/ReentrancyGuard.js
```diff
@@ -0,0 +1,31 @@
+'use strict';
+import expectThrow from './helpers/expectThrow';
+const ReentrancyMock = artifacts.require('./helper/ReentrancyMock.sol');
+const ReentrancyAttack = artifacts.require('./helper/ReentrancyAttack.sol');
+
+contract('ReentrancyGuard', function(accounts) {
+  let reentrancyMock;
+
+  beforeEach(async function() {
+    reentrancyMock = await ReentrancyMock.new();
+    let initialCounter = await reentrancyMock.counter();
+    assert.equal(initialCounter, 0);
+  });
+
+  it('should not allow remote callback', async function() {
+    let attacker = await ReentrancyAttack.new();
+    await expectThrow(reentrancyMock.countAndCall(attacker.address));
+  });
+
+  // The following are more side-effects that intended behaviour:
+  // I put them here as documentation, and to monitor any changes
+  // in the side-effects.
+
+  it('should not allow local recursion', async function() {
+    await expectThrow(reentrancyMock.countLocalRecursive(10));
+  });
+
+  it('should not allow indirect local recursion', async function() {
+    await expectThrow(reentrancyMock.countThisRecursive(10));
+  });
+});
```

### test/helpers/ReentrancyAttack.sol
```diff
@@ -0,0 +1,11 @@
+pragma solidity ^0.4.8;
+
+contract ReentrancyAttack {
+
+  function callSender(bytes4 data) {
+    if(!msg.sender.call(data)) {
+      throw;
+    }
+  }
+
+}
```

### test/helpers/ReentrancyMock.sol
```diff
@@ -0,0 +1,46 @@
+pragma solidity ^0.4.8;
+
+import '../../contracts/ReentrancyGuard.sol';
+import './ReentrancyAttack.sol';
+
+contract ReentrancyMock is ReentrancyGuard {
+
+  uint256 public counter;
+
+  function ReentrancyMock() {
+    counter = 0;
+  }
+
+  function count() private {
+    counter += 1;
+  }
+
+  function countLocalRecursive(uint n) public nonReentrant {
+    if(n > 0) {
+      count();
+      countLocalRecursive(n - 1);
+    }
+  }
+
+  function countThisRecursive(uint256 n) public nonReentrant {
+    bytes4 func = bytes4(keccak256("countThisRecursive(uint256)"));
+    if(n > 0) {
+      count();
+      bool result = this.call(func, n - 1);
+      if(result != true) {
+        throw;
+      }
+    }
+  }
+
+  function countAndCall(ReentrancyAttack attacker) public nonReentrant {
+    count();
+    bytes4 func = bytes4(keccak256("callback()"));
+    attacker.callSender(func);
+  }
+
+  function callback() external nonReentrant {
+    count();
+  }
+
+}
```

### test/helpers/expectThrow.js
```diff
@@ -0,0 +1,20 @@
+export default async promise => {
+  try {
+    await promise;
+  } catch (error) {
+    // TODO: Check jump destination to destinguish between a throw
+    //       and an actual invalid jump.
+    const invalidJump = error.message.search('invalid JUMP') >= 0;
+    // TODO: When we contract A calls contract B, and B throws, instead
+    //       of an 'invalid jump', we get an 'out of gas' error. How do
+    //       we distinguish this from an actual out of gas event? (The
+    //       testrpc log actually show an 'invalid jump' event.)
+    const outOfGas = error.message.search('out of gas') >= 0;
+    assert(
+      invalidJump || outOfGas,
+      "Expected throw, got '" + error + "' instead",
+    );
+    return;
+  }
+  assert.fail('Expected throw not received');
+};
```
