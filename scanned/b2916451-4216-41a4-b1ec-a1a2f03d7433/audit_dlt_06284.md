# [M] `payable` modifier on function without use of native currency can lead to locked ETH

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-28
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/40
Type: hats-finding

## Details
**Github username:** @rokinot
**Twitter username:** rokinot
**Submission hash (on-chain):** 0x7bd0178024ef370a50fb73e962b71535c69768c2e7c8960660892f4409680dce
**Severity:** medium

**Description:**
**Description**\
As described by the [OpenZeppelin's report](https://blog.openzeppelin.com/ion-protocol-audit#locked-eth-in-contract), `payable` functions with no use of ether can lead to locked funds. However, the report, as well as the fix commit, missed a function: `flashLeverageWethAndSwap()` at `UniswapFlashloanBalancerSwapHandler.sol`, which can be found [here](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/flash/handlers/base/UniswapFlashloanBalancerSwapHandler.sol#L91).

The functions in the aforementioned report have the unnecessary payable modifiers, which were subsequently patched in a commit, but the main branch still includes the modifier in them as well as the competition's version of the code. I'm pointing this out as to make sure the developers are aware of this version control ambiguity.

**Revised Code File**\
Remove the modifier. Running the unit and fuzz tests will show the system still works as intended.

```solidity
    function flashLeverageWethAndSwap(
        uint256 initialDeposit,
        uint256 resultingAdditionalCollateral,
        uint256 maxResultingAdditionalDebt,
        uint256 deadline,
        bytes32[] calldata proof
    )
        external
        checkDeadline(deadline)
        onlyWhitelistedBorrowers(proof)
    {
```
