# [H] H-2 Undeﬁned behavior for mint

## Summary
Severity: High
Contest weight: 0.5412
Dataset id: 7922
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In FantiumMinterV1.mint(), param to is intended to be to Address to be the minted token's owner. It's wrong because the ﬁnal mint will be for msg.sender (FantiumMinterV1.sol#L269). athlete -> 0x90F79bf6EB2c4f870365E785982E1f101E93b906 fan -> 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65
```solidity
await minterContract.connect(fan).mint(athlete.address, 1, { value: 100000000000000 });
console.log("ownerOf -> ", await nftContract.ownerOf(1000000));
```
print fan -> 0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65

## Recommendation
We recommend changing it: fantiumNFTContract.mintTo(_to, thisTokenId);
