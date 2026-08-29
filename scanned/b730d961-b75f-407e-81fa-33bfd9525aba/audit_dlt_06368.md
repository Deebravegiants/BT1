# [H] LootVoteController.sol#_clearExpiredProxies() - wrong array handling can lead to expired proxies remaining uncleared,  unexpected reverts

## Summary
Severity: High
Chain: Smart contract
Component: Paladin
Published: 2024-02-07
Source: https://github.com/hats-finance/Paladin-0x1610bfde27e57b068af7f38aec3d2a7b1d146989/issues/11
Type: hats-finding

## Details
**Github username:** @PlamenTSV
**Twitter username:** @p_tsanev
**Submission hash (on-chain):** 0xc67fc6f1195f84696e6f13badb11a46bbd024982bd24321e8d23082dd6f1c501
**Severity:** high

**Description:**
**Description**\
The function ``_clearExpiredProxies`` holds the meaning of it's name - to clear past proxies provided a user, thus freeing his blocked power for these proxies.
Due to poor array handling, some proxies could remain uncleared or the function might always revert

**Attack Scenario**\
I will explain it through an example:
We save the current ``currentUserProxyVoters[user]`` in a memory variable ``proxies``. Then we cache the length of ``proxies``, for example 5. We cache the last index of ``proxies``, in our case 4.
Then we begin the loop:
Let's say proxy with index 0 is fine.
Proxy with index 1 is expired. Then we delete the info for that proxy voter and unblock the power. 1 is not the last index, so we swap index 1 and 4 and pop. So now the element at the last position of the array came at index 1, but the array's i still increments, meaning we essentially skip over the element that held the previous last place (index 4 became the new index 1 but we never check it again).

The other even worse scenario is the array length. We cache the length of the ``proxies`` to be 5. But it is a memory variable. When we do ``currentUserProxyVoters[user].pop()``, the length of the proxy voters will become 4, but the cached length would remain 5. Thus when we reach the last element we can: 1. Run into an out of bounds error or 2. pop an element that was previously non-expired since it is the last available element.


**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

Recommendation: there are 2 fixes needed her:
1. When we find an element that is expired, do not increment i so that you do not skip proxies
2. Do not cache the length of the memory variable, but of the storage one.
