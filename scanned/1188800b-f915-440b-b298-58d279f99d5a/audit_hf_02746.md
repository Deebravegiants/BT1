# [M] Potential avoidance of liquidation

## Summary
Severity: Medium
Contest weight: 0.6954
Dataset id: 15078
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can deposit ERC721 tokens using the MarginTrading::provideERC721 function, which can then be used as collateral for borrowing. Additionally, users can execute the MarginTrading::exercise function to convert their ERC721 into baseToken value, crediting the respective marginAccount.
The issue arises when a malicious user deposits ERC721 tokens that are invalid within the protocol context; i.e., they are inactive, expired, or worthless:
File: HegicModule.sol
```solidity
function checkValidityERC721(uint id) external returns(bool) {
    if (getPayOffAmount(id) > 0 && isOptionActive(id) && getExpirationTime(id) > block.timestamp) {
        return true;
    }
}
```
Consider the following scenario:
1. A user deposits several invalid ERC721 tokens (that pay nothing, are inactive, or have expired) using the MarginTrading::provideERC721.
2. The user is eligible for liquidation, and a liquidator invokes the MarginTrading::liquidate function, which retrieves the ERC721 tokens at MarginAccount#L228:
File: MarginAccount.sol
```solidity
function liquidate(
    uint marginAccountID,
    address baseToken,
    address marginAccountOwner
) external onlyRole(MARGIN_TRADING_ROLE) {
    for(uint i; i < availableErc721.length; i++) {
        uint[] memory erc721TokensByContract = erc721ByContract[marginAccountID][availableErc721[i]];
        erc721Params[i] = IModularSwapRouter.ERC721PositionInfo(availableErc721[i], baseToken, marginAccountOwner, erc721TokensByContract);
        delete erc721ByContract[marginAccountID][availableErc721[i]];
    }
    uint amountOutInUSDC = modularSwapRouter.liquidate(erc20Params,erc721Params);
    erc20ByContract[marginAccountID][baseToken] += amountOutInUSDC;
    _clearDebtsWithPools(marginAccountID, baseToken);
}
```
3. Each token ID is then individually checked in HegicModule#L46:
File: HegicModule.sol
```solidity
function liquidate(
    uint[] memory value,
    address holder
) external onlyRole(MODULAR_SWAP_ROUTER_ROLE) {
    for (uint i; i < value.length; i++) {
        if (getPayOffAmount(value[i]) > 0 && isOptionActive(value[i]) && getExpirationTime(value[i]) > block.timestamp) {
            uint profit = getOptionValue(value[i]);
            hegicPositionManager.transferFrom(marginAccount, address(this), value[i]);
            operationalTreasury.payOff(value[i], marginAccount);
            amountOut += assetExchangerUSDCetoUSDC.swapInput(profit, 0);
            hegicPositionManager.transferFrom(address(this), holder, value[i]);
        }
    }
}
```
This results in the liquidation process being more costly and complex as the user introduces more invalid token IDs.
The following test demonstrates how a token ID that was exercised can be reintroduced into the MarginAccount, which is unnecessary as the token ID will not be usable in future liquidations nor can it be withdrawn (This is an example of how a user can obtain invalid ERC721s; they may obtain invalid ERC721s from another source):
```solidity
describe("Exercise: provide exercised ERC721", async () => {
    let optionId: bigint
    let marginAccountID: bigint
    it("exercise: provide exercised ERC721", async () => {
        // 1. Provide ERC721 to the marginAccount
        await c.MarginAccountManager.connect(c.deployer).createMarginAccount()
        optionId = BigInt(0)
        marginAccountID = BigInt(0)
        await c.MarginTrading.connect(c.deployer).provideERC721(
            marginAccountID,
            await c.HegicPositionsManager.getAddress(),
            optionId)
        expect(await c.HegicPositionsManager.ownerOf(optionId)).to.be.eq(await c.MarginAccount.getAddress());
        // 1. Excercise a ERC721
        expect(await c.MarginAccount.getErc20ByContract(marginAccountID, c.USDC.getAddress())).to.be.eq(BigInt(0))
        expect(await c.MarginAccount.getErc20ByContract(marginAccountID, c.HegicPositionsManager.getAddress())).to.be.eql([BigInt(0)])
        await c.MarginTrading.connect(c.deployer).exercise(
            marginAccountID, await c.HegicPositionsManager.getAddress(), optionId)
        expect(await c.MarginTrading.calculateMarginAccountValue.staticCall(marginAccountID)).to.be.eq(marginAccountValue)
        expect(await c.MarginAccount.getErc20ByContract(marginAccountID, c.USDC.getAddress())).to.be.eq(marginAccountValue)
        expect(await c.MarginAccount.getErc20ByContract(marginAccountID, c.HegicPositionsManager.getAddress())).to.be.eql([])
        // 2. Provide again the same exercised ERC721 to the marginAccount
        expect(await c.HegicPositionsManager.ownerOf(optionId)).to.be.eq(await c.deployer.getAddress());
        await c.HegicPositionsManager.approve(await c.MarginAccount.getAddress(), optionId)
        await c.MarginTrading.connect(c.deployer).provideERC721(
            marginAccountID,
            await c.HegicPositionsManager.getAddress(),
            optionId)
        // 3. MarginAccount has an exercised ERC721 that is unusable. Additionally the ERC721 can't be withdrawn
        expect(await c.MarginAccount.getErc20ByContract(marginAccountID, c.HegicPositionsManager.getAddress())).to.be.eql([BigInt(0)])
        expect(await c.HegicPositionsManager.ownerOf(optionId)).to.be.eq(await c.MarginAccount.getAddress());
        await expect(
            c.MarginTrading.connect(c.deployer).withdrawERC721(
                marginAccountID, await c.HegicPositionsManager.getAddress(), optionId)
        ).to.be.revertedWith("token id is not valid")
```

## Recommendation
It is recommended that MarginTrading::provideERC721 only accept token IDs that are valid:
File: MarginTrading.sol
```solidity
function provideERC721(
    uint marginAccountID,
    address token,
    uint collateralTokenID
) external nonReentrant onlyApprovedOrOwner(marginAccountID) {
    require(modularSwapRouter.checkValidityERC721(token, BASE_TOKEN, collateralTokenID), "token id is not valid");
    marginAccount.provideERC721(marginAccountID, msg.sender, token, collateralTokenID, BASE_TOKEN);
    emit ProvideERC721(marginAccountID, msg.sender, token, collateralTokenID);
}
```
