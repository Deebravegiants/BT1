# [M] wstX.sol contract deposit(), mint(), withdraw() and redeem() functions are not incomplaince with ERC4626

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-11
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/65
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x2b1e989f7e706213581585c76a599ab7c9b5daa5dac1eefd1d23626837dbe6d4
**Severity:** medium

**Description:**
### Title
`wstX.sol` contract `deposit()`, `mint()`, `withdraw()` and `redeem()` functions are not incomplaince with `ERC4626`

### Severity
Medium

### Affected contracts
wrstMTRG.sol, wstARB.sol, wstDOJ.sol, wstMANTA.sol, wstMETIS.sol, wstROSE.sol, wstVLX.sol, wstZETA.sol and wstToken.sol

### Vulnerability details
`wstX` has used solmate's ERC4626 as base contract. `wstX` contracts herein referred as `wstTokenV2.sol` mentions to be ERC4626 fully compliant which can be checked [here](https://github.com/AccumulatedFinance/contracts-v2/blob/ef89e73c9d86f086dfc9dd379cb395c1368642cd/contracts/wstTokenV2.sol#L884) and [here](https://github.com/AccumulatedFinance/contracts-v2/blob/ef89e73c9d86f086dfc9dd379cb395c1368642cd/contracts/wstTokenV2.sol#L1050)

>     It is fully compatible with [ERC4626](https://eips.ethereum.org/EIPS/eip-4626) allowing for DeFi composability

>     wstToken adheres to ERC-4626 vault specs 

The `deposit()`, `withdraw()`, `redeem()` and `mint()` functions of `wstX` contract is not incompliance with ERC4626.

For understanding:

Lets check `redeem()` function which is used to redeem a specific number of shares from owner and sends assets of underlying token from the vault to receiver and it is implemented as:

```solidity
    function redeem(
        uint256 shares,
        address receiver,
        address owner
    ) public virtual returns (uint256 assets) {
        if (msg.sender != owner) {
            uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

            if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/65_
