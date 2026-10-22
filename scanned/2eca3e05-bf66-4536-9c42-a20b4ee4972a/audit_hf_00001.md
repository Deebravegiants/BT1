# [M] Invalid Slippage Control in FlashProtocol::flashStake()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 8
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FlashProtocol contract provides a public stake() function for users to stake principal tokens and mint the corresponding amount of fToken to the users. The users-staked funds are transferred to the FlashStrategy to earn yields. The fToken can be burned by the stakers to claim yields earned by the FlashStrategy. To facilitate the yield claiming for users, the FlashProtocol contract also provides an external flashStake() function in which the acts of staking, minting fToken and burning all fToken are done in one transaction.  
In the following, we examine the FlashProtocol::flashStake() routine that is designed to provide the staker with instant upfront yield within one transaction. We notice the actual burn fToken and claim yield operation IFlashStrategy(_strategyAddress).burnFToken() essentially specifies no restriction on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller return (line 293). Note the way to use the quotedReturn parameter is invalid as it is eventually computed from IFlashStrategy(_strategyAddress).quoteBurnFToken() (line 289). In other words, the IFlashStrategy(_strategyAddress).quoteBurnFToken() output guarantees tokensOwed=_minimumReturned  
```solidity
function flashStake(
    address _strategyAddress,
    uint256 _tokenAmount,
    uint256 _stakeDuration,
    address _yieldTo,
    bool _mintNFT
) external nonReentrant {
    // Stake
    uint256 fTokensMinted = stake(_strategyAddress, _tokenAmount, _stakeDuration, _yieldTo, _mintNFT).fTokensToUser;
    IERC20C fToken = IERC20C(strategies[_strategyAddress].fTokenAddress);
    fToken.transferFrom(msg.sender, address(this), fTokensMinted);
    // Quote, approve, burn
    uint256 quotedReturn = IFlashStrategy(_strategyAddress).quoteBurnFToken(fTokensMinted);
    // Approve and send yield to specified address
    fToken.approve(_strategyAddress, fTokensMinted);
    IFlashStrategy(_strategyAddress).burnFToken(fTokensMinted, quotedReturn, _yieldTo);
}
```

## Recommendation
Develop an effective mitigation to the above front-running attack to better protect the interests of users.
