# [H] Improper Logic Of VirtualTrade::sell()

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 12777
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Plutos VirtualTrade protocol, the Entry contract allows the user to deposit the supported stable_token and get in return the virtual stablecoin (i.e., chip token). Meanwhile, the VirtualTrade contract allows the user to buy the virtual assets with chip token and sell the virtual assets to get chip token. The user can profit from the rise or fall of the virtual assets (The prices of the virtual assets vary with the prices of the real assets). In particular, the VirtualTrade::sell() routine allows the user to sell the specified virtual asset to get chip token. While examining its logic, we notice there is an improper implementation that needs to be improved. To elaborate, we show below the related code snippet of the VirtualTrade contract. At the beginning of the sell() routine, the statement (i.e., uint256 chip_amount = asset.position[owner].safeMul(oracle.get_asset_price(name)).safeDiv(1e18)) (line 67) is executed to calculate the amount of the chip token that the user can receive by selling the certain amount (specified by the input amount parameter) of the virtual asset (specified by the input name parameter). However, we notice the asset.position[owner] that saves the user's total amount of the specified virtual asset rather than the input amount is incorrectly used in the above calculation, which directly undermines the assumption of the design. Given this, we suggest to correct the implementation as below: uint256 chip_amount = amount.safeMul(oracle.get_asset_price(name)).safeDiv(1e18) (line 67).
```solidity
function sell(string memory name, uint256 amount, uint256 min_rec, address owner) public returns(uint256){
    asset_info storage asset = all_assets[name];
    require(asset.exist, "invalid asset");
    require(owner == msg.sender || allowed[owner][msg.sender], "permission denied");
    require(asset.position[owner] >= amount, "not enough position");
    uint256 chip_amount = asset.position[owner].safeMul(oracle.get_asset_price(name)).safeDiv(1e18);
    require(chip_amount >= min_rec, "Sell slippage");
    uint256 before = asset.position[owner];
    asset.position[owner] = before.safeSub(amount);
    asset.total_position = asset.total_position.safeSub(amount);
    asset.invest[owner] = asset.invest[owner].safeMul(asset.position[owner]).safeDiv(before);
    TokenInterface(chip).generateTokens(owner, chip_amount);
    emit AssetSell(name, owner, chip_amount, amount);
    return chip_amount;
}
```

## Recommendation
Correct the implementation of the sell() routine as above-mentioned.
