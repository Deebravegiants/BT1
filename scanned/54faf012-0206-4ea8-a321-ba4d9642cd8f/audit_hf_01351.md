# [H] Add checks to xcall()

## Summary
Severity: High
Contest weight: 0.5756
Dataset id: 6803
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function xcall() does some sanity checks, nevertheless more checks should be added to prevent issues later on in the use of the protocol. If _args.recovery == 0 then _sendToRecovery() will send funds to the 0 address, effectively losing them. If _params.agent == 0 the forceReceiveLocal can’t be used and funds might be locked forever. The _args.params.destinationDomain should never be s.domain, although this is also implicitly checked via _mustHaveRemote() assuming a correct configuration. If _args.params.slippageTol is set to something greater than s.LIQUIDITY_FEE_DENOMINATOR then funds can be locked as xcall() allows for the user to provide the local asset, avoiding any swap while _handleExecuteLiquidity() in execute() may attempt to perform a swap on the destination chain.
```solidity
function xcall(XCallArgs calldata _args) external payable nonReentrant whenNotPaused returns (bytes32) {
    // Sanity checks.
    ...
}
```

## Recommendation
Consider adding the following checks:
• recovery != 0.
• agent != 0.
• _args.params.destinationDomain != s.domain.
• _args.params.slippageTol <= s.LIQUIDITY_FEE_DENOMINATOR.
Also doublecheck if any additional checks are useful.
