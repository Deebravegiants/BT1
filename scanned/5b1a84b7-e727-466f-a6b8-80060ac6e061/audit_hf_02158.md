# [H] Improper Logic Of VaultKeeperFeed::deposit()

## Summary
Severity: High
Contest weight: 0.6357
Dataset id: 12074
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
By design, the VaultKeeperFeed contract is the main entry for interaction with the FeedVault contract. In particular, one entry routine, i.e., deposit(), accepts the deposits of the supported token assets and then deposits the assets to FeedVault (specified by the vaultAddress). While examining its logic, we notice the share calculation is incorrect. To elaborate, we show below the related code snippet of the VaultKeeperFeed contract. In the deposit() function, the following statement is executed to calculate the share for the deposit: _shares = (_amount.mul(totalShares)).div(_before) (line 90). We notice totalShares represents the total shares held by all the depositors of the VaultKeeperFeed contract, which is corresponding to the total balance of the token deposited to the VaultKeeperFeed contract. However, _before stores the total balance of the token deposited to the vaultAddress rather than the VaultKeeperFeed contract (line 70), which directly undermines the deposit() design.
```solidity
function deposit(uint256 _amount) external nonReentrant {
    // Balance before deposit
    uint256 _before = balance();
    // Transfer token from sender
    token.safeTransferFrom(msg.sender, address(this), _amount);
    // Deposit token to target vault
    token.approve(vaultAddress, _amount);
    IFeedVault(vaultAddress).deposit(_amount);
    // Balance after deposited
    uint256 _after = balance();
    // Additional check for deflationary tokens
    _amount = _after.sub(_before);
    // Calculate shares to be added
    uint256 _shares = 0;
    if (totalShares == 0) {
        _shares = _amount;
    } else {
        _shares = (_amount.mul(totalShares)).div(_before);
    }
    // Get user info from storage
    UserInfo storage user = userInfo[address(msg.sender)];
    // Add shares to total shares
    totalShares = totalShares.add(_shares);
    // Add shares to user info
    user.shares = user.shares.add(_shares);
    // Emit Deposited event
    emit Deposited(_amount);
```

## Recommendation
Correct the implementation of the deposit() routine as above-mentioned.
