# [M] Improve dexAllowlist

## Summary
Severity: Medium
Contest weight: 0.4268
Dataset id: 9649
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The functions _executeSwaps() of both SwapperV2.sol and Swapper.sol use a whitelist to make sure the right functions in the allowed dexes are called.
The checks for approveTo, callTo and signature (callData) are independent. This means that any signature is valid for any dex combined with any approveTo address. This grands more access than necessary.
This is important because multiple functions can have the same signature. For example these two functions have the same signature:
• gasprice_bit_ether(int128)
• transferFrom(address,address,uint256)
See bytes4_signature=0x23b872dd Note: brute forcing an innocent looking function is straightforward
The transferFrom() is especially dangerous because it allows sweeping tokens from other users that have set an allowance for the LiFi Diamond. If someone gets a dex whitelisted, which contains a function with the same signature then this can be abused in the current code.
Present in both SwapperV2.sol and Swapper.sol:
```solidity
function _executeSwaps(...) ... {
    ...
    if (
        !(appStorage.dexAllowlist[currentSwapData.approveTo] &&
        appStorage.dexAllowlist[currentSwapData.callTo] &&
        appStorage.dexFuncSignatureAllowList[bytes32(currentSwapData.callData[:8])])
    ) revert ContractCallNotAllowed();
    ...
}
```

## Recommendation
In the whitelisting manager DexManagerFacet.sol, combine the dex_address, approveTo and signature as a set and whitelist them as a triple. Adapt the rest of the code (e.g. SwapperV2.sol and Swapper.sol) to match that.
