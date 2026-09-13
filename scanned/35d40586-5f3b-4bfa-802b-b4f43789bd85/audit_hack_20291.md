# [C] **5.1.2 Overflow in** SegmentedSegmentTree

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** SegmentedSegmentTree464.sol#L
**Description:** SegmentedSegmentTree464.updateneeds to perform an overflow check in case the new value is
greater than the old value. This overflow check is done when adding the new difference to each node in each
layer (usingaddClean). Furthermore, there's a final overflow check by adding up all nodes in the first layer in
total(core).
However, intotal, the nodes in individual groups are added usingDirtyUint64.sumPackedUnsafe:
function total(Core storage core) internal view returns (uint64) {
return DirtyUint64.sumPackedUnsafe(core.layers[0][0], 0, _C)
+ DirtyUint64.sumPackedUnsafe(core.layers[0][1], 0, _C);
}

The nodes in a group can overflow without triggering an overflow & revert. The impact is that the order book depth
and claim functionalities break for all users.


```
// SPDX-License-Identifier: BUSL-1.
pragma solidity ^0.8.0;
import "forge-std/Test.sol";
import "forge-std/StdJson.sol";
import "../../contracts/mocks/SegmentedSegmentTree464Wrapper.sol";
contract SegmentedSegmentTree464Test is Test {
using stdJson for string;
uint32 private constant _MAX_ORDER = 2**15;
SegmentedSegmentTree464Wrapper testWrapper;
function setUp() public {
testWrapper = new SegmentedSegmentTree464Wrapper();
}
function testTotalOverflow() public {
uint64 half64 = type(uint64).max / 2 + 1;
testWrapper.update(0, half64);
// map to the right node of layer 0, group 0
testWrapper.update(_MAX_ORDER / 2 - 1, half64);
assertEq(testWrapper.total(), 0);
}
}
```
**Recommendation:** Perform a safe addition for the first layer and rewrite the overflow check.
// DirtyUint64.sumPackedSafe still needs to be implemented and should do checked addition
require(
uint256(DirtyUint64.sumPackedSafe(core.layers[0][0], 0, _C))
+ uint256(DirtyUint64.sumPackedSafe(core.layers[0][1], 0, _C)) <= type(uint64).max,
"TREE_MAX"
);

**Clober:** Fixed in PR 40.
**Spearbit:** Verified. The fix checks whether the new updated value can cause an overflow and throws the error
early preventing such operations.
