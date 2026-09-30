# [H] Proper Update of user.lastClaim in veMNT::deposit()

## Summary
Severity: High
Contest weight: 0.6161
Dataset id: 12497
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the MantisSwap protocol, the veMNT contract provides the functionalities for users to deposit MNT and claim veMNT. The claimable amount of the veMNT is calculated per the deposit amount of MNT, the reward rate, and the time elapses since the last claim. To elaborate, we show below the code snippet of the deposit() routine. As the name indicates, it is used for users to deposit MNT in the contact. Specially, for a new user's deposit, the reward rate (veMntRate) is set to veMntPerSec (line 100). So, if the user further deposits based on the current deposit, it will update the reward rate based on the new total deposit amount (line 104). This is because the current deposit is rewarded with the current veMntRate, while the new deposit will be rewarded with the veMntPerSec. However, it comes to our attention that there is a lack of updating the lastClaim variable based on the new veMntRate and the new total deposit amount. As a result, following a claim operation, the user may claim more veMNT than it is expected.
```solidity
function deposit(uint256 amount) external checkCaller nonReentrant {
    require(amount > 0, "Cannot be 0");
    mntLp.safeTransferFrom(msg.sender, address(this), amount);
    UserData memory user = userData[msg.sender];
    if (user.amount == 0) {
        user.veMntRate = veMntPerSec;
        user.lastClaim = block.timestamp;
        user.amount = amount;
    } else {
        uint256 newRate = _getNewRate(user, amount, veMntPerSec);
        user.veMntRate = newRate;
        Public
        user.amount += amount;
    }
    userData[msg.sender] = user;
    emit Deposit(msg.sender, amount);
}
```

## Recommendation
Revisit the deposit() routine to update the lastClaim state accordingly per the new amount and the new veMntRate.
