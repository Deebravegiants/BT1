# [M] CPC Fee Collection From Unknowing Users

## Summary
Severity: Medium
Contest weight: 0.4481
Dataset id: 11824
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the core of the Copycat protocol is the CopycatLeader contract that allows for non-contract users to add assets into the protocol and get minted with the corresponding pool share. While reviewing the share minting logic, we notice the required LeaderDepositCopycatFee collection is flawed. To elaborate, we show below the related depositTo() function. It implements a rather straightforward logic in transferring user assets into the contract and mint the corresponding pool share. It comes to our attention the associated copycat fee for the deposit is collected from the given argument to, instead of msg.sender. As a result, an unknowing user may be charged for the deposit fee.
```solidity
function depositTo(address to, uint256 percentage, IERC20 refToken, uint256 maxRefAmount) payable public virtual nonReentrant onlyEOA returns(uint256 totalShare) {
    require(!disabled, "D");
    uint256 refAmount = 0;
    uint256 bnbBefore = address(this).balance;
    ICopycatAdapter[] memory adapters = S.getAdapters(address(this));
    uint256 depositCopycatFee = S.getLeaderDepositCopycatFee(address(this));
    if(depositCopycatFee > 0 && msg.sender != address(factory) && to != owner()){
        S.collectLeaderFee(to, depositCopycatFee);
    }
    for(uint i = 0; i < tokens.length; i++) {
        IERC20 token = tokens[i];
        uint256 amount = token.balanceOf(address(this)) * percentage / 1e18;
        if(amount > 0) {
            if(i > 0 || msg.value == 0) {
                token.transferFrom(msg.sender, address(this), amount);
            } else {
                WETH.deposit{value: amount}();
                if(token == refToken) {
                    refAmount += amount;
                }
            }
        }
    }
}
```

## Recommendation
Properly revise the above depositTo() routine to collect deposit fee from msg.sender, instead of the user-provided argument to.
