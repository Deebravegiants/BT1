# [M] Function `restructureCapTable

## Summary
Severity: Medium
Contest weight: 0.4071
Dataset id: 18393
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the function that is intended to wipe the token holdings of a list of addresses during a cap‑table restructuring. The code iterates over the addressesToWipe array but mistakenly reads the element at index 0 on every iteration (address current = addressesToWipe[0];). As a result, only the first address in the array is actually burned, while the remaining addresses are ignored. The root cause is a typographical error that substitutes the loop variable i with a constant index, a classic off‑by‑one/incorrect‑index bug. An attacker or a careless operator can trigger the function with an array containing multiple addresses, expecting all of them to be cleared. Because the contract only burns the first address repeatedly, the other participants retain their token balances. From a user perspective the expected outcome – a zero balance for every address supplied – does not materialise; some users still see their tokens, leading to confusion such as 'my balance should be zero after the restructure but it isn’t'. The impact is primarily accounting‑related: the cap table no longer reflects the intended ownership distribution, which may affect voting rights, dividend calculations, or downstream protocol logic that assumes those addresses hold no tokens. The bug manifests whenever restructureCapTable is called with an addressesToWipe array longer than one element, which is a normal scenario for a multi‑party restructuring. The affected parties are token holders whose balances should be cleared, the protocol that relies on accurate equity calculations, and any downstream contracts that read the token supply. The issue was discovered during a manual code audit that inspected the loop logic and noticed the constant index. It can be hard to notice because the function may still succeed (the first burn works) and no explicit revert occurs; the problem only becomes visible when checking the balances of the other addresses after the call. The bug belongs to the class of 'incorrect loop indexing' or 'logic error in array handling'. The correct fix is to replace the constant addressesToWipe[0] with the loop variable addressesToWipe[i], ensuring each address in the array is processed exactly once. After the fix, the function will burn the full balance of every supplied address, aligning the on‑chain state with the intended cap‑table restructuring and preventing residual token holdings.

## Proof of Concept
Here, in L313, addressToWipe[0] only takes first address of the array. While ignoring the rest and also since first address’s tokens are burned it will fail `addressesToWipe` array has more than one addresses.
```solidity
function restructureCapTable(address[] calldata helpers, address[] calldata addressesToWipe) public {
    require(zchf.equity() < MINIMUM_EQUITY);
    checkQualified(msg.sender, helpers);
    for (uint256 i = 0; i < addressesToWipe.length; i++){
        address current = addressesToWipe[0];
        _burn(current, balanceOf(current));
    }
}
```

## Recommendation
Change `address current = addressesToWipe[0];` ==> `address current = addressesToWipe[i];`
