# [M] DOS when using `addPriorityStakers`

## Summary
Severity: Medium
Contest weight: 0.7368
Dataset id: 17965
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a logic error in the addPriorityStakers function that can cause a denial‑of‑service (DoS) condition. Inside a for‑loop the contract checks `if (i > 0 && staker < _priorityStakers[i‑1]) revert DuplicateArrayElements();`. This condition compares the numeric value of two consecutive addresses and reverts when the later address is numerically smaller than the previous one. Because Ethereum addresses have no natural ordering requirement, any unordered pair of addresses has roughly a 50 % chance of triggering the revert. The custom error name suggests a duplicate‑array check, but the code actually enforces an unnecessary ascending order. The root cause is a misplaced comparison that was likely intended to detect duplicate entries, yet duplicates are harmless – writing the same address to `isPriorityStaker` multiple times only wastes gas. When the condition is met, the transaction aborts before any `isPriorityStaker[staker] = true` assignments or `PriorityStakerRegistered` events occur, leaving the priority‑staker list unchanged. From a user’s perspective the expected outcome – successful registration of priority stakers – is replaced by an unexpected revert with the error `DuplicateArrayElements`, consuming gas without any state change. This can be exploited by submitting a list of addresses deliberately ordered to fail, or even unintentionally by a legitimate caller whose address order happens to be descending, effectively blocking the addition of priority stakers and degrading protocol availability. No assets are directly at risk, but the protocol’s ability to manage privileged participants is impaired, which may affect downstream reward distribution or governance mechanisms. The issue was discovered during a formal audit and reproduced on Remix by feeding two random addresses; the transaction succeeded only when the first address was greater than the second. The bug is subtle because the revert occurs only for certain permutations, making it appear intermittent and hard to reproduce without systematic testing. The recommended remediation is to remove the ordering check entirely, as duplicates do not affect correctness, or replace it with a proper duplicate detection that does not rely on address ordering. By eliminating the faulty revert, the function will always succeed in registering the supplied priority stakers, restoring expected behavior and preventing the DoS scenario.

## Proof of Concept
There’s the following condition in the `_addPriorityStakers` function at [L626](https://github.com/Certora/2023-01-blockswap-fv/blob/certora/certora/munged/syndicate/Syndicate.sol#L626):

File: Syndicate.sol
    
```solidity
623:         for (uint256 i; i < numOfStakers; ++i) {
624:             address staker = _priorityStakers[i];
625: 
626:             if (i > 0 && staker < _priorityStakers[i-1]) revert DuplicateArrayElements(); 
627: 
628:             isPriorityStaker[staker] = true; 
629: 
630:             emit PriorityStakerRegistered(staker);
631:         }
```

As we can see here, after the index 0, it will revert if the address at index i is less than the address at index i - 1, which is quite an odd condition. Additionally, the custom error is `DuplicateArrayElements`, which doesn’t match with what the written condition is checking.

When adding, as an example, any 2 addresses as Priority Stakers, whether one address is computed to be greater or less than the previous one shouldn’t matter (any permutation of those 2 addresses should enable these 2 addresses to be added as Priority Stakers). We can guess here that the condition was badly implemented, making so that adding a list of Priority Stakers has a 50% chance of failing.

You can try the following on Remix by inputting 2 random addresses and see that this can be true or false depending on the order, hence the 50% chance of failure claim:
    
```solidity
    function addrCompare(address a1, address a2) external pure returns (bool) {
        return a1 < a2;
    }
```

The following rule catches it as it’s unreachable with the bug (original code), and passes without it (suggested remediation):
    
```solidity
rule addingTwoDifferentPriorityStackers(address _priorityStaker1, address _priorityStaker2) {
    // Excluding address(0)
    require(_priorityStaker1 != 0 && _priorityStaker2 != 0);
    // Avoiding duplicates and making sure the address at index i - 1 is greater than the address at index i
    require(_priorityStaker1 > _priorityStaker2);
    // Making sure they aren't already Priority Stakers
    require(!isPriorityStaker(_priorityStaker1) && !isPriorityStaker(_priorityStaker2));
    env e;

    // Adding any 2 Priority stakers address
    addPriorityStakers(e, _priorityStaker1, _priorityStaker2);
    // The rule will fail due to this assertion being unreachable with the bug
    assert(true, "This is unreacheable");
}
```

## Recommendation
My guess is that here, the developer wanted to somehow report that the address list contains a mistake.

However, here, even if there were duplicates in the array, this wouldn’t change anything regarding the final state (just some gas would be wasted with multiple SSTOREs). I’d advise against checking if the value is already set in storage before writing to it, as multiple SLOADs can make the function call quite gas heavy very fast.

The real condition was probably intended to be “if the staker’s index isn’t equal to the current index then revert”, but for that you’d need a way to fetch an index in an array (like JavaScript’s indexOf), which isn’t the case in Solidity.

The simplest and best solution here is simply to remove the line:
    
File: Syndicate.sol
```solidity
623:         for (uint256 i; i < numOfStakers; ++i) {
624:             address staker = _priorityStakers[i];
625: 
- 626:             if (i > 0 && staker < _priorityStakers[i-1]) revert DuplicateArrayElements(); 
627: 
628:             isPriorityStaker[staker] = true; 
629: 
630:             emit PriorityStakerRegistered(staker);
631:         }
```

Again, there’s no impact besides wasting gas in adding a Priority Staker multiple times, so this revert shouldn’t exist in my opinion

**vince0656 (Blockswap) commented:**  

Assessment: Low/Medium

We will instead check `isPriorityStaker[staker]` and revert if true - thanks.

**Dravee (warden) commented:**  

Hey there @vince0656,

Just curious: why revert at all? There’s no harm in writing several times in storage `isPriorityStaker[staker]` = true with a wrong input. However, “checking `isPriorityStaker[staker]` and revert if true” will penalize every caller as all these storage reading operations are expensive.

I don’t believe the happy path should cost more gas just to prevent an unhappy one.

But that’s really just a suggestion on the remediation.

Edit:  
I’ll also add here that a DOS (it can be worked around here but this is still a degraded functionality, with a damaged availability) is Medium Severity usually on code4rena’s documentation, not low, due to “the function of the protocol or its availability could be impacted”:
 
> 2 — Med: Assets not at direct risk, but the function of the protocol or its availability could be impacted, or leak value with a hypothetical attack path with stated assumptions, but external requirements.

I also ask here if you could please reconsider this as just Medium 👍. Of course, I’ll accept any final decision you make.

**teryanarmen (Certora) commented:**  

I think there are two separate issues here. I believe the failure to check for duplicate entries is Low/Informational severity as having duplicates in the `_priorityStakers` array has no effect on the protocol. The check being unnecessary and causing a DOS to me is medium severity.
