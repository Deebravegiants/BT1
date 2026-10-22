# [C] 5.1.3 _delegatecall_uint256_arr_arg_returns_uint256wrong calldata encoding

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk

**Context:** DelegateCalls.sol#L26-L

**Description:** TheDelegatecallslibrary is used by theYieldManagerto delegatecall into aYieldProvider. The
calldata encoding for most of the_delegatecall_*functions is excessive (uses more calldata bytes than needed)
or incorrect:

- Theabi.encodePackedfunction is used to encode the calldata, using a 256-bit selector argument when 4
    bytes are enough.
- The_delegatecall_uint256_arg_returns_uint256can write into unallocated memory inreturndata-
    copy(ptr, 0, size)ifsize > 0x24.
- The _delegatecall_uint256_arr_arg_returns_uint256 encodes the calldata as
    abi.encodePacked(selector, uint256[] arg) which leads to an incorrect calldata encod-
    ing:

```
0x00-0x20: selector
0x20-0x40: arg[0]
0x40-0x60: arg[1]
// ...
```
But this should be abi encoded, i.e.,abi.encodeWithSelector(bytes4(bytes32(selector)), arg)should give
you the correct result:

```
aabbccdd// selector
0000000000000000000000000000000000000000000000000000000000000020 // arr offset
0000000000000000000000000000000000000000000000000000000000000002 // arr length
0000000000000000000000000000000000000000000000000000000000001337 // arr[0]
0000000000000000000000000000000000000000000000000000000000001338 // arr[1]
```
Currently, the YieldProvider.claim(uint256[] calldata requestIds) calls are all performed with
an empty requestedIds no matter what requestedIds the calling YieldManager defined. The Yield-
Manager.claimPending(uint256 idx, address providerAddress, uint256[] requestIds) calling
LidoYieldProvider.claim(requestIds)will not actually perform a withdrawal from Lido. It's impossible to claim
the unstaked funds from Lido, preventing L2 to L1 withdrawals.

**Recommendation:** Considerl cleaning up the functions in the DelegateCalls library and using
abi.encodeWithSelector(selector, args)everywhere instead of hand-crafting the calldata:

```
// always use encodeWithSelector with an optional argument
```
- abi.encodePacked(selector, arg)
+ abi.encodeWithSelector(bytes4(bytes32(selector)), arg)

Alternatively, directly define the interface for the desired functions:


# DRAFT

```
// pseudo code
```
- function _delegatecall_uint256_arr_arg_returns_uint256(address provider, uint256 selector, uint256[]
    ,! memory arg) internal returns (uint256) {
- (bool success, bytes memory res) = provider.delegatecall(abi.encodePacked(selector, arg));
- require(success, "delegatecall failed");
- return abi.decode(res, (uint256));
- }

```
+ interface IDelegateCalls {
+ function claim(uint256[] calldata requestIds) external returns (uint256 claimed);
+ // ...
+ }
```
```
+ function _delegatecall_claim(address provider, uint256[] memory arg) internal returns (uint256) {
+ (bool success, bytes memory res) = provider.delegatecall(abi.encodeCall(IDelegateCalls.claim,
,! (arg)));
+ require(success, "delegatecall failed");
+ return abi.decode(res, (uint256));
+ }
```
Consider adding mainnet fork integration tests with the actual protocols. TheYieldManager.t.sol:test_claim-
Pending_Lido_succeedscurrently passes because theMockLidoWithdrawalQueue.claimWithdrawalsignores
the array parameters.
