# [H] Certain cost models may be exploited with callback tokens

## Summary
Severity: High
Contest weight: 0.0782
Dataset id: 5017
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
At the moment, the Set's sell() function first makes an external call in order to transfer the refund to receiver_ and only afterwards calls the cost mode's update() function. Under a specific configuration where the asset has receive-callbacks (e.g., an ERC777 token) and the cost model used by a Set's market is stateful (ie. actually makes use of update() function calls) this might be vulnerable to reentrancy: Upon receiving the tokens, the receiver_ might exploit the fact that the cost model has not been updated yet by calling back into the Set.

## Recommendation
One of the following can be done:
• Consider reversing the order of external calls. Set owners are very powerful and users of that set have decided that the owners are trustworthy. Set owner are also the only party being able to specify a market's cost model. A user would assume that the owner they trust will not specify malicious contracts as cost models, therefore calls made to a model's update() function are unlikely to exploit the Set by reentering. Calling update() before transferring the tokens will therefore ensure that the call made to a untrusted 3rd party (the receiver_) is the very last interaction of the sell() function and no incomplete state can be exploited.
• Document this issue publicly for future Set creators. Alternatively, this issue should be publicly documented so that creators of Sets can make sure to either not use assets that have hooks, or to not make use of cost models that are stateful and make use of the update() function call. As part of the security review we prepared an example Token Integration Checklist that can be used to document this issue.
