# [H] 5.2.5 Paused state can’t be set and thereforewithdrawQuote()can’t be executed

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk

**Context:** InvariantCheck, LeveragedPool, PoolCommitter

**Description:** ThecheckInvariants()function of theInvariantCheckcontract is called via the modifierscheck-
InvariantsBeforeFunction()andcheckInvariantsAfterFunction()of bothLeveragedPoolandPoolCommit-
tercontracts, and it is meant to pause the contracts if the invariant checks don’t hold.

The aforementioned modifiers also contain therequire(!paused, "Pool is paused");statement, which reverts
the entire transaction and resets thepausedvariable that was just set.

Furthermore, thepausedstate can only be set by theInvariantCheckcontract due to theonlyInvariantCheck-
Contractmodifier. Thus thepausedvariable will never be set totrue, makingwithdrawQuote()impossible to be
executed because it requires the contract to be paused.

This means that the quote tokens will always stay in the pool even if invariants don’t hold and all other actions are
blocked.

Relevant parts of the code:

ThecheckInvariants()function callsInvariantCheck.pause()if the invariants don’t hold. The latter calls
pause()inLeveragedPoolandPoolCommitter:

```
contract InvariantCheck is IInvariantCheck {
function checkInvariants(address poolToCheck) external override {
...
pause(IPausable(poolToCheck), IPausable(address(poolCommitter)));
...
}
function pause(IPausable pool, IPausable poolCommitter) internal {
pool.pause();
poolCommitter.pause();
}
}
```
In LeveragedPool and PoolCommitter contracts, the checkInvariantsBeforeFunction() and checkIn-
variantsAfterFunction()modifiers will make the transaction revert ifcheckInvariants()sets the paused
state.

```
contract LeveragedPool is ILeveragedPool, Initializable, IPausable {
modifier checkInvariantsBeforeFunction() {
invariantCheck.checkInvariants(address(this));// can set paused to true
require(!paused, "Pool is paused");// will reset pause again
_;
}
modifier checkInvariantsAfterFunction() {
require(!paused, "Pool is paused");
_;
invariantCheck.checkInvariants(address(this));// can set paused to true
require(!paused, "Pool is paused");// will reset pause again
}
function pause() external override onlyInvariantCheckContract { // can only called from
,! InvariantCheck
paused = true;
emit Paused();
}
}
```

```
contract PoolCommitter is IPoolCommitter, Initializable {
modifier checkInvariantsBeforeFunction() {
invariantCheck.checkInvariants(leveragedPool);// can set paused to true
require(!paused, "Pool is paused"); // will reset pause again
_;
}
modifier checkInvariantsAfterFunction() {
require(!paused, "Pool is paused");
_;
invariantCheck.checkInvariants(leveragedPool);// can set paused to true
require(!paused, "Pool is paused");// will reset pause again
}
function pause() external onlyInvariantCheckContract { // can only called from InvariantCheck
paused = true;
emit Paused();
}
```
**Recommendation:** This issue is also discussed in modifiers-undermine-contract-pausing and there are a few
reasons to reconsider fixing it:

- When a transaction triggers an invariant check and it is rolled back due to the revert, other transactions might
    still be executed. With a paused state this wouldn’t happen.
- Pause functionality that doesn’t work is misleading for developers and code reviewers. It is better to delete
    the dead code, which also saves gas.
- withdrawQuote()cannot be executed since the pause state is unreachable.

If it is preferable to use the pause functionality, it can be done by having a surrounding contract which stores the
pause state and calls the underlying logic with atrymechanism. The underlying logic can then be reverted while
the surrounding contract keeps thepausedstate.

Here is an implementation example of a surrounding contract that handles the revert and sets thepausevariable.
The code that checks the invariants reverts with theInvariantsFail()custom error, which is caught by the
try/catchblock in the caller and the paused state is set.


```
//SPDX-License-Identifier: MIT
pragma solidity 0.8.11;
import "hardhat/console.sol";
```
```
contract Pool {
error InvariantsFail();
function DoSomething() public pure {
revert InvariantsFail();
}
}
contract InvariantCheck {
Pool myPool = new Pool();
bool pause;
function TryDoSomething() public returns (string memory) {
try myPool.DoSomething() { return "Ok"; }
catch Error(string memory reason) { return reason; }
catch Panic(uint) { return "Panic"; }
catch (bytes memory reason) {
if (bytes4(reason) == bytes4(abi.encodeWithSignature("InvariantsFail()"))) {
pause = true;
return("InvariantsFail");
}
return "Unknown";
}
}
constructor() {
console.log("Pause =",pause);
console.log(TryDoSomething());
console.log("Pause =",pause);
}
}
```
Note: Beware that this does not interfere with any other functionality. ETH has to be sent back to the caller as this
will not be automatically reverted.

**Tracer:** We decided to change how invariant checking works. Instead of checking the invariants on every function
call, we now have a contract which can be called at any time by an EOA to do the same invariant checks/pausing.

This obviously does not have the same invariant guarantees, as it requires an EOA to start a TX to detect invariant
violations, but we decided to make the tradeoff anyway. However, it does mean that this issue should not be
relevant anymore, because the paused state can in fact be set.

Addressed in PR 384.

**Spearbit:** Acknowledged.
