# [H] DoS: `claimForAllWindows`

## Summary
Severity: High
Contest weight: 0.8118
Dataset id: 1904
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the value of `currentWindow` is raised sufficiently high `Splitter.claimForAllWindows()` will not be able to be called due to the block gas limit.

`currentWindow` can only ever be incremented and thus will always increase. This value will naturally increase as royalties are paid into the contract.

Furthermore, an attacker can continually increment `currentWindow` by calling `incrementWindow()`. An attacker can impersonate a `IRoyaltyVault` and send 1 WEI worth of WETH to pass the required checks.

## Proof of Concept
Excerpt from `Splitter.claimForAllWindows()` demonstrating the for loop over `currentWindow` that will grow indefinitely.
    
```solidity
for (uint256 i = 0; i < currentWindow; i++) {
    if (!isClaimed(msg.sender, i)) {
        setClaimed(msg.sender, i);

        amount += scaleAmountByPercentage(
            balanceForWindow[i],
            percentageAllocation
        );
    }
}
```

`Splitter.incrementWindow()` may be called by an attacker increasing `currentWindow`.
    
```solidity
function incrementWindow(uint256 royaltyAmount) public returns (bool) {
    uint256 wethBalance;

    require(
        IRoyaltyVault(msg.sender).supportsInterface(IID_IROYALTY),
        "Royalty Vault not supported"
    );
    require(
        IRoyaltyVault(msg.sender).getSplitter() == address(this),
        "Unauthorised to increment window"
    );

    wethBalance = IERC20(splitAsset).balanceOf(address(this));
    require(wethBalance >= royaltyAmount, "Insufficient funds");

    require(royaltyAmount > 0, "No additional funds for window");
    balanceForWindow.push(royaltyAmount);
    currentWindow += 1;
    emit WindowIncremented(currentWindow, royaltyAmount);
    return true;
}
```

## Recommendation
Consider modifying the function `claimForAllWindows()` to instead claim for range of windows. Pass the function a `startWindow` and `endWindow` and only iterate through windows in that range. Ensure that `endWindow < currentWindow`.

In my opinion, the severity level should be 3 (High Risk) instead of 2 (Med Risk) duplicate of #3 

While similar, I believe these issues are separate.

Issue 3 indicates that the check that `msg.sender` is an authorized `RoyaltyVault` is faulty, since any contract can implement the interface and return the `Splitter` from `getSplitter`. While this should be fixed, as the warden suggested in the Recommended Mitigation Steps in #3, the issue raised in this issue can still occur when enough authorized `RoyaltyVault` contracts call `incrementWindow`.

`claimForAllWindows` can remain, but as this warden suggests, a `claimForWindows(uint256 startWindow, uint256 endWindow, uint256 percentageAllocation, bytes32[] calldata merkleProof)` should exist, in case `claimForAllWindows` becomes prohibitively expensive, even organically (i.e. `currentWindow` is made very high due to sufficient authorized `incrementWindow` calls).
