# [M] `StargateStrategy#_withdraw`: ether becomes trapped in the contract whenever a user withdraws

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1519
Type: code-finding

## Details
# Lines of code

 https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/stargate/StargateStrategy.sol#L259


# Vulnerability details

## Impact

Upon withdrawing funds from `StargateStrategy`, due to an incorrect assumption in `_withdraw`, the full amount is not refunded but instead remains in the contract as native ETH, resulting in a loss of funds for the withdrawing user.

## Proof of Concept

We will assume here that `amount > queued` and the code inside the `if` statement is executed.

In `_withdraw`, the amount of LP tokens to withdraw is stored as `toWithdraw`, and withdrawn by calling `lpStaking.withdraw` (L252). Then, the Stargate Router is used to redeem these LP tokens and receive native ETH (L253-L257). The ether is wrapped (L259) and sent to the `to` address specified as a parameter (L266).

The problem is that the code assumes that the amount of ETH received after calling `router.instantRedeemLocal` is equal to the amount of LP tokens redeemed (`toWithdraw`), which is not necessarily the case (and indeed not likely). Since only `toWithdraw` amount of ETH is wrapped, the remainder is left in the contract after the transaction completes, resulting in a loss of funds for the user.

```solidity
File: tapioca-yieldbox-strategies-audit\contracts\stargate\StargateStrategy.sol

241:     function _withdraw(
242:         address to,
243:         uint256 amount
244:     ) internal override nonReentrant {
245:         uint256 available = _currentBalance();
246:         require(available >= amount, "StargateStrategy: amount not valid");
247: 
248:         uint256 queued = wrappedNative.balanceOf(address(this));
249:         if (amount > queued) {
250:             compound("");
251:             uint256 toWithdraw = amount - queued;
252:             lpStaking.withdraw(lpStakingPid, toWithdraw);
253:             router.instantRedeemLocal(
254:                 uint16(lpRouterPid),
255:                 toWithdraw,
256:                 address(this)
257:             );
258: 
259:             INative(address(wrappedNative)).deposit{value: toWithdraw}(); // @audit incorrectly assuming toWithdraw = amount of ETH received
260:         }
261: 
262:         require(
263:             amount <= wrappedNative.balanceOf(address(this)),
264:             "Stargate: not enough"
265:         );
266:         wrappedNative.safeTransfer(to, amount);
267: 
268:         emit AmountWithdrawn(to, amount);
269:     }
```

To prove this, in `stargateStrategy-fork.test.ts`, alter the test titled `"should allow deposits and withdrawals"` to observe the ETH balance of the `StargateStrategy` contract before and after the indended execution flow has concluded:

```diff
    it('should allow deposits and withdrawals', async () => {
        const {
            stargateStrategy,
            weth,
            wethAssetId,
            yieldBox,
            deployer,
            binanceWallet,
            timeTravel,
        } = await loadFixture(registerFork);

+       console.log((await ethers.provider.getBalance(stargateStrategy.address)).toString());

        const routerEth = await stargateStrategy.addLiquidityRouter();
        const lpStakingContract = await ethers.getContractAt(
            'ILPStaking',
            await stargateStrategy.lpStaking(),
        );
        const lpStakingPid = await stargateStrategy.lpStakingPid();

        const poolInfo = await lpStakingContract.poolInfo(
            await stargateStrategy.lpStakingPid(),
        );
        const lpToken = await ethers.getContractAt(
            '@openzeppelin/contracts/token/ERC20/IERC20.sol:IERC20',
            poolInfo[0],
        );

        await yieldBox.registerAsset(
            1,
            weth.address,
            stargateStrategy.address,
            0,
        );

        const wethStrategyAssetId = await yieldBox.ids(
            1,
            weth.address,
            stargateStrategy.address,
            0,
        );
        expect(wethStrategyAssetId).to.not.eq(wethAssetId);
        const assetsCount = await yieldBox.assetCount();
        const assetInfo = await yieldBox.assets(assetsCount.sub(1));
        expect(assetInfo.tokenType).to.eq(1);
        expect(assetInfo.contractAddress.toLowerCase()).to.eq(
            weth.address.toLowerCase(),
        );
        expect(assetInfo.strategy.toLowerCase()).to.eq(
            stargateStrategy.address.toLowerCase(),
        );
        expect(assetInfo.tokenId).to.eq(0);

        const amount = ethers.BigNumber.from((1e18).toString()).mul(10);

        await weth
            .connect(binanceWallet)
            .transfer(deployer.address, amount.mul(10));

        await weth.approve(yieldBox.address, ethers.constants.MaxUint256);

        let share = await yieldBox.toShare(wethStrategyAssetId, amount, false);
        await yieldBox.depositAsset(
            wethStrategyAssetId,
            deployer.address,
            deployer.address,
            0,
            share,
        );

        let strategyWethBalance = await weth.balanceOf(
            stargateStrategy.address,
        );

        const lpStakingBalance = (
            await lpStakingContract.userInfo(
                lpStakingPid,
                stargateStrategy.address,
            )
        )[0];

        expect(strategyWethBalance.eq(0)).to.be.true;
        expect(lpStakingBalance.gt(0)).to.be.true;
        timeTravel(100 * 86400);
        share = await yieldBox.balanceOf(deployer.address, wethStrategyAssetId);
        await yieldBox.withdraw(
            wethStrategyAssetId,
            deployer.address,
            deployer.address,
            0,
            share,
        );
        strategyWethBalance = await weth.balanceOf(stargateStrategy.address);
        expect(strategyWethBalance.eq(0)).to.be.true;
        
+       console.log((await ethers.provider.getBalance(stargateStrategy.address)).toString());
    });
```

The output shows that indeed some ETH remains in the contract after the user deposits and withdraws the same amount:
```
  StargateStrategy fork test
0
816151744885982
    ✔ should allow deposits and withdrawals (5587ms)


  1 passing (7s)
```

## Tools Used

Manual review, hardhat

## Recommended Mitigation Steps

Change `_withdraw` to unwrap the correct amount of ETH:

```diff
    function _withdraw(
        address to,
        uint256 amount
    ) internal override nonReentrant {
        uint256 available = _currentBalance();
        require(available >= amount, "StargateStrategy: amount not valid");

        uint256 queued = wrappedNative.balanceOf(address(this));
        if (amount > queued) {
            compound("");
            uint256 toWithdraw = amount - queued;
            lpStaking.withdraw(lpStakingPid, toWithdraw);
            router.instantRedeemLocal(
                uint16(lpRouterPid),
                toWithdraw,
                address(this)
            );

-           INative(address(wrappedNative)).deposit{value: toWithdraw}();
+           INative(address(wrappedNative)).deposit{value: address(this).balance}();
        }

        require(
            amount <= wrappedNative.balanceOf(address(this)),
            "Stargate: not enough"
        );
        wrappedNative.safeTransfer(to, amount);

        emit AmountWithdrawn(to, amount);
    }
```


## Assessed type

Math
