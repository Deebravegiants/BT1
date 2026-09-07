# [M] StableSwapFactory can't pause PoolDeployers

## Summary
Severity: Medium
Chain: Smart contract
Component: Thorn-protocol
Published: 2024-10-03
Source: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/14
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x82792b8b1868c1aa91f3b330832154a1d26d19fa29f3a17ab2e89ff227ffb9b7
**Severity:** medium

**Description:**
**Description**\
`StableSwapTwoPoolDeployer` and `StableSwapThreePoolDeployer` are pausable contracts and have `pause/unpause` functions exposed.

```solidity
contract StableSwapThreePoolDeployer is Ownable,Pausable {
    uint256 public constant N_COINS = 3;

    constructor(){}

    function pauseContract() external onlyOwner(){ _pause();}

    function unPauseContract() external onlyOwner(){ _unpause();}
```

But since the StableSwapFactory will be the owner of the Deployer, because it called the `createSwapPair` function here:

```solidity
contract StableSwapFactory  {

function createSwapPair(
    address _tokenA,
    address _tokenB,
    uint256 _A,
    uint256 _fee,
    uint256 _admin_fee
) external onlyAdmin {
   
    require(_tokenA != ZEROADDRESS && _tokenB != ZEROADDRESS && _tokenA != _tokenB, "Illegal token");
    (address t0, address t1) = sortTokens(_tokenA, _tokenB);
    address LP = LPFactory.createSwapLP(t0, t1, ZEROADDRESS, address(this));
    address swapContract = SwapTwoPoolDeployer.createSwapPair(t0, t1, _A, _fee, _admin_fee, msg.sender, LP); <-----------
    IStableSwapLP(LP).setMinter(swapContract);
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Thorn-protocol-0x1286ecdac50215a366458a14968fbca4bd95067d/issues/14_
