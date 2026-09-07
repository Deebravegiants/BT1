# [M] StableSwapTwoPoolDeployer::createSwapPair is missing whenNotPaused modifier

## Summary
Severity: Medium
Chain: Smart contract
Component: Thorn-protocol
Published: 2024-10-03
Source: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/11
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x583b3a6802966b63ea69ff06445baf91abc0d509afef998d359eb6198c369eca
**Severity:** medium

**Description:**
**Description**\
`SwapTwoPoolDeployer`, `SwapThreePoolDeployer` and `StableSwapLPFactory` are pausable contract but only `SwapThreePoolDeployer` applies `whenNotPaused` modifer.

```solidity
// SwapThreePoolDeployer

function createSwapPair(
        address _tokenA,
        address _tokenB,
        address _tokenC,
        uint256 _A,
        uint256 _fee,
        uint256 _admin_fee,
        address _admin,
        address _LP
    ) external onlyOwner whenNotPaused returns (address) {
    
    
// StableSwapLPFactory
  
function createSwapLP(
        address _tokenA,
        address _tokenB,
        address _tokenC,
        address _minter
    ) external onlyOwner returns (address) {
```

Because of that even when the contacts are paused, this function will not be paused then the whole idea of Pausable is lost.

**Attack Scenario**\
Describe how the vulnerability can be exploited.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/11_
