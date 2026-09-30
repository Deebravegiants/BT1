# [M] Suggested Use Of nonReentrant In mint()

## Summary
Severity: Medium
Contest weight: 0.4590
Dataset id: 11774
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A common coding best practice in Solidity is the adherence of checks-effects-interactions principle. This principle is eﬀective in mitigating a serious attack vector known as re-entrancy. Via this particular attack vector, a malicious contract can be reentering a vulnerable contract in a nested manner. Speciﬁcally, it ﬁrst calls a function in the vulnerable contract, but before the ﬁrst instance of the function call is ﬁnished, second call can be arranged to re-enter the vulnerable contract by invoking functions that should only be executed once. We notice there are several occasions the checks-effects-interactions principle is violated. For example, the mint() function (see the code snippet below) is provided to externally call several token contracts to transfer assets. However, the invocation of an external contract requires extra care in avoiding the above re-entrancy.

```solidity
function mint(uint256 amount) public {
    address owner = msg.sender;
    uint256 mintedPUSD = amount.mul(getPOLPrice()).div(getStakeRate()).div(1000000);
    _minted[owner] = _minted[owner].add(mintedPUSD);
    setMinted(owner, getMinted(owner).add(mintedPUSD));
    uint256 bonusPNX = mintedPUSD.mul(1000000).mul(getBonusRate()).div(100).div(getPNXPrice());
    // _bonus[owner] = _bonus[owner].add(bonusPNX);
    setBonus(owner, getBonus(owner).add(bonusPNX));
    _staked[owner] = _staked[owner].add(amount);
    setStaked(owner, getStaked(owner).add(amount));
    polToken.transferFrom(owner, polPoolAddr, amount);
    pUSDToken.transferFrom(pusdPoolAddr, owner, mintedPUSD);
    transferPUSDTo(owner, mintedPUSD);
    pnxToken.transferFrom(pnxPoolAddr, pnxOfficialAddress, bonusPNX * 15 / 100);
    transferPNXTo(pnxOfficialAddress, bonusPNX.mul(15).div(85));
}
```

Apparently, the interaction with the external contract (line 88) starts before eﬀecting the update on internal states (line 82), hence violating the principle. In this particular case, if the external contract has certain hidden logic that may be capable of launching re-entrancy via the very same mint() function.

## Recommendation
Add the nonReentrant modiﬁer to prevent reentrancy.
