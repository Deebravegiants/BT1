# [M] Improved Quote Between depositToken and LP

## Summary
Severity: Medium
Contest weight: 0.5932
Dataset id: 12474
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the WombatStaking contract interacts with Wombat Exchange to facilitate users to deposit assets in Wombat and stake the LP in MasterWombat for yield. Moreover, the WombatStaking contract allows users to deposit Wombat LP into MasterWombat for yield. To incentivize users deposit in WombatStaking, it mints receiptToken to users who can further deposit the receiptToken into MasterMagpie for additional rewards.

To elaborate, we show below the code snippet of the depositLP() routine. As the name indicates, it is designed for users to deposit Wombat LP. Per current design, the amount of receiptToken to mint is the same as the amount of the depositToken. Therefore, in order to get the intended amount of receiptToken for the deposit of Wombat LP, it needs to calculate the amount of the depositToken (line 348). To achieve that, the contract implements the getDepositTokenAmtByLP() routine (as the code shown below) by referring to the logic in Wombat. However, it comes to our attention that the amount returned from the getDepositTokenAmtByLP() routine is in WAD, not in the decimals of the depositToken! To correct, there's a need to convert the decimals from WAD to the decimals of the depositToken. Our analysis shows that Wombat provides an official interface, i.e., quotePotentialWithdraw(), which can be used to get the amount of the depositToken for the given amount of LP token.
```solidity
function depositLP(
    address _lpAddress,
    uint256 _lpAmount,
    address _for
)
    nonReentrant
    whenNotPaused
    _onlyActivePoolHelper(_lpAddress)
    external
{
    // Get information of the Pool of the token
    Pool storage poolInfo = pools[_lpAddress];
    // Transfer lp to this contract and stake it to wombat
    IERC20(poolInfo.lpAddress).safeTransferFrom(_for, address(this), _lpAmount);
    _toMasterWomAndSendReward(_lpAddress, _lpAmount, true); // triggers harvest from wombat exchange
    // update variables
    uint256 caledDepositTokenAmount =
        getDepositTokenAmtByLP(_lpAmount, poolInfo.lpAddress, poolInfo.depositTarget);
    Public
    uint256 receiptTokenToMint = getSharesForDepositTokens(caledDepositTokenAmount, _lpAddress);
    IMintableERC20(poolInfo.receiptToken).mint(msg.sender, receiptTokenToMint);
    // ...
}

function getDepositTokenAmtByLP(uint256 _amount, address _lpToken, address _depositTarget)
    public
    view
    returns(uint256 amount)
{
    IAsset asset = IAsset(_lpToken);
    require(asset.totalSupply() > 0 && asset.liability() > 0, "Insufficient liquidity");
    uint256 ampFactor = IWombatPool(_depositTarget).ampFactor();
    uint256 liabilityToBurn = (asset.liability() * _amount) / asset.totalSupply();
    amount = withdrawalAmountInEquilImpl(
        int256(liabilityToBurn),
        int256(uint256(asset.cash())),
        int256(uint256(asset.liability())),
        int256(ampFactor)
    ).toUint256();
}
```
Similarly, as shown in the following code snippet, the withdraw() routine invokes a getLPTokensForShares() routine (line 372) to get the amount of LP token to withdraw from MasterWombat. Our analysis shows that Wombat also provides an interface, i.e., quotePotentialDeposit(), which can be used to get the amount of LP token for the given amount of the depositToken.
```solidity
function withdraw(
    address _lpToken,
    uint256 _amount,
    uint256 _minAmount,
    address _sender
)
    nonReentrant
    whenNotPaused
    _onlyPoolHelper(_lpToken)
    external
{
    // _amount is the amount of stable
    Pool storage poolInfo = pools[_lpToken];
    uint256 sharesAmount = getSharesForDepositTokens(_amount, _lpToken);
    uint256 lpAmount = getLPTokensForShares(sharesAmount, _lpToken);
    IERC20(poolInfo.lpAddress).approve(poolInfo.depositTarget, lpAmount);
    _toMasterWomAndSendReward(_lpToken, lpAmount, false);
    Public
    uint256 beforeWithdraw = IERC20(poolInfo.depositToken).balanceOf(address(this));
    IWombatPool(poolInfo.depositTarget).withdraw(
        poolInfo.depositToken,
        lpAmount,
        _minAmount,
        address(this),
        block.timestamp
    );
    // ...
}
```

## Recommendation
Properly use the correct Wombat interfaces to quote between the depositToken and the LP token.
