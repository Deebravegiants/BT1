# [H] Malicious actor can steal funds using dex and data arguments in swapFromDexAndBond

## Summary
Severity: High
Contest weight: 0.5657
Dataset id: 22754
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Attacker can supply arbitrary dex and data arguments to swapFromDexAndBond that will steal funds of zapper users and the zapper itself. swapFromDexAndBond allows the user to provide a user defined dex address and data. contractsV2/contracts/zap/Zapper.sol#L79
```solidity
function swapFromDexAndBond(
    address tokenAddr,
    uint256 amount,
    address dex,
    uint256 tokenMinimum,
    bytes memory data
) public returns (bool) {
    dex.functionCall(data);
}
```
Therefore a malicious actor can make any arbitrary call and:
1. Steal funds other user funds by calling transferFrom on tokens approved to the zapper. Zapper requires users to approve ERC20 tokens to it before calling its swap functions. (High likelihood, High impact)
2. Steal dormant funds in zapper by calling approve or transfer with their address on tokens such as WETH. (Low likelihood, Low impact)
Theft of funds

## Recommendation
Whitelist allowed dexs.
