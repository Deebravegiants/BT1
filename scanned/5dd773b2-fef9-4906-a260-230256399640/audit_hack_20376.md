# [H] 5.2.3 WETHRebasingshare price precision issue breaks ERC20 invariants

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** WETHRebasing.sol#L

**Description:** TheWETHRebasingshare price is dynamically defined as:

```
(address(this).balance - _totalVoidAndRemainders) / _totalShares
```
In certain cases, when a share is split into two remainder balances, the share price can increase. This happens
due to precision issues in this calculation. The_totalSharesdecreases by 1 but the_totalVoidAndRemainders
might only decrease by therounded-downshare price amount, resulting in the share price increasing by 1. The
increase in share price can lead to balances andtotalAssetsunexpectedly increasing and breaking core ERC
invariants that users/contracts rely on:

- post-transfer:balanceOf(from) -= amount; balanceOf(to) += amountas well astotalSupply() +=
    amount.
- post-claim:balanceOf(recipient) += claimedAmount;.
- deposit,withdraw,transfer,claim,configureshould not change thesharePrice.

**Recommendation:** The share price should not change in any of thedeposit,withdraw,transfer,claim,con-
figurefunctions. It should only change when new ETH yield is distributed (or when any other ETH donation to
the contract happens). Consider keeping track of the share price explicitly and only increasing it when new yield
comes in, similar to how USDB and rebasing ETH work.

**Example:**

```
address(this).balance = 109
_totalVoidAndRemainders = 0
_totalShares = 10
sharePrice = floor(109 / 10) = floor(10.9) = 10
```
Atransfers 5 toB,A's 1 share (valued at a share price of 10) is split up into 2 remainders of 5. New state:

```
address(this).balance = 109
_totalVoidAndRemainders = 10
_totalShares = 9
sharePrice = floor((109 - 10) / 9) = floor(11) = 11
```
**Proof of Concept:**

Logs:

```
=== totalSupply === 60004
=== sharePrice === 15001
=== totalSupply === 60007
=== sharePrice === 15002
Error: !bob
Error: a == b not satisfied [uint]
Left: 15004
Right: 15003
```
```
// SPDX-License-Identifier: MIT
pragma solidity 0.8.15;
```
```
// Testing utilities
import { Test, StdUtils } from "forge-std/Test.sol";
import { WETHRebasing } from "src/L2/WETHRebasing.sol";
import { Shares } from "src/L2/Shares.sol";
import { Blast } from "src/L2/Blast.sol";
import { Gas } from "src/L2/Gas.sol";
```

```
DRAFT
```
import { Predeploys } from "src/libraries/Predeploys.sol";

// WETHRebasing.t.sol
import { YieldMode } from "src/L2/ERC20Rebasing.sol";
import { MockYield } from "test/CommonTest.t.sol";
import { console2 } from "forge-std/console2.sol";

contract SpearbitTest is Test {
address constant alice = address(0x1337);
address constant bob = address(0x1338);
Shares SHARES;
WETHRebasing internal WETH;

```
function setUp() public virtual {
vm.label(alice, "alice");
vm.label(bob, "bob");
```
```
vm.etch(Predeploys.GAS, address(new Gas(address(this), Predeploys.BLAST, address(0), 0, 1, 1,
,! 2, 2)).code);
MockYield mockYield = new MockYield();
vm.etch(Predeploys.BLAST, address(new Blast(Predeploys.GAS, address(mockYield))).code);
```
```
Shares shares = new Shares({ _price: 1e4, _reporter: address(0) });
vm.etch(Predeploys.SHARES, address(shares).code);
SHARES = Shares(Predeploys.SHARES);
SHARES.initialize(1e4);
vm.label(address(SHARES), "SHARES");
```
```
vm.deal(address(this), 100 ether);
WETH = new WETHRebasing();
vm.etch(Predeploys.WETH_REBASING, address(WETH).code);
WETH = WETHRebasing(payable(Predeploys.WETH_REBASING));
WETH.initialize{ value: shares.price() }();
vm.label(address(WETH), "WETH");
}
```
```
function addBalance(address account, uint256 amount) internal {
vm.deal(account, account.balance + amount);
}
```
```
function test_Claim_invariants() public {
claim_invariants(30000, 20007);
}
```
```
function claim_invariants(uint256 balance, uint256 claim) internal {
addBalance(alice, balance);
vm.startPrank(alice);
WETH.configure(YieldMode.CLAIMABLE);
WETH.deposit{value: balance}();
vm.stopPrank();
```
```
addBalance(address(WETH), claim);
```
```
vm.startPrank(alice);
uint256 claimable = WETH.getClaimableAmount(alice);
// 4*15,001+0 == 60,
console2.log("=== totalSupply ===", WETH.totalSupply());
console2.log("=== sharePrice ===", WETH.sharePrice());
WETH.claim(bob, claimable);
// 3*15,002+14,999+2 == 60,
console2.log("=== totalSupply ===", WETH.totalSupply());
console2.log("=== sharePrice ===", WETH.sharePrice());
```

# DRAFT

```
vm.stopPrank();
```
```
assertEq(WETH.balanceOf(alice), balance, "!alice");
assertEq(WETH.balanceOf(bob), claimable, "!bob");
}
}
```
Also works with a simple transfer:

```
function test_transfer_invariants() public {
uint248 balance = 30_000;
uint248 yield = 20_007;
uint248 toTransfer = yield;
vm.assume(balance > 0);
```
```
addBalance(alice, balance);
vm.startPrank(alice);
WETH.configure(YieldMode.CLAIMABLE);
WETH.deposit{value: balance}();
vm.stopPrank();
```
```
addBalance(address(WETH), yield);
```
```
vm.startPrank(alice);
WETH.transfer(bob, toTransfer);
vm.stopPrank();
```
```
assertEq(WETH.balanceOf(alice), balance - toTransfer, "!alice");
assertEq(WETH.balanceOf(bob), toTransfer, "!bob");
}
```
**Blast:** I think we can take some inspiration from how we handle this problem for the native ether on the L2 to solve
this precision issue. In op-geth, the share price for ether only changes when new yield comes in, and it can never
change due to user actions like deposits/withdrawals/transfers/shares converting to remainder.
