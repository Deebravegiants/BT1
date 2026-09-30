# [M] Unsecure `transferFrom`

## Summary
Severity: Medium
Contest weight: 0.6057
Dataset id: 13222
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the transferFrom function of the Yieldy token contract. In this function the contract validates a caller's permission to move tokens by checking the stored allowance value (_allowances[_from][msg.sender] >= _value). However, the actual amount that is deducted from the sender’s balance is not the raw token amount but a derived credit amount calculated by the internal creditsForTokenBalance(_value) function. The contract then subtracts this credit amount from creditBalances[_from] without verifying that the sender’s credit balance is sufficient. Because the allowance check does not reflect the real credit balance, an attacker can supply a _value that is lower than the approved allowance but higher than the sender’s true token balance. The subsequent subtraction can under‑flow, causing the sender’s credit balance to wrap around to a very large number and effectively mint credits for the recipient. This under‑flow may be silently prevented by compiler‑generated overflow checks in some Solidity versions, but those checks are not guaranteed across compiler releases, meaning the safety of the operation is unintentionally delegated to the compiler configuration. The bug can be triggered whenever a spender is granted an allowance that exceeds the holder’s actual token balance and the holder’s credit balance is insufficient for the requested transfer. Users affected are token holders who rely on the contract to enforce accurate balances; the protocol itself suffers accounting errors, potential loss of funds, and a breach of trust in the token’s accounting logic. The issue was discovered during a formal security audit when the code was examined and the mismatch between allowance verification and credit balance deduction was identified. It is hard to notice because the allowance check appears correct at first glance, and because modern Solidity compilers may silently insert overflow protections that hide the under‑flow during testing. To remediate the issue the contract should validate the sender’s credit balance against the required credit amount (e.g., require(creditBalances[_from] >= creditAmount)) or redesign the transfer logic to work directly with token balances, employing explicit safe‑math operations and avoiding reliance on compiler‑specific checks. In practical terms, a user attempting a transfer that should fail may instead see the transaction succeed, their displayed token balance unchanged or incorrectly increased, and the recipient receiving more credits than justified, effectively causing funds to disappear from the system or appear out of thin air, which violates the protocol’s accounting assumptions.

## Proof of Concept
The `allowance` of an account does not have to reflect the real balance of an account, however in the `transferFrom` method, it is the value that is checked in order to verify that the user has enough balance to make the transfer.
```solidity
function transferFrom(
    address _from,
    address _to,
    uint256 _value
) public override returns (bool) {
    require(_allowances[_from][msg.sender] >= _value, "Allowance too low");
```

However, the real balance of the `Yieldy` contract is based on the calculation made by the `creditsForTokenBalance` method, so an underflow could be made in the subtraction of the balance of the `from` account.
```solidity
uint256 creditAmount = creditsForTokenBalance(_value);
creditBalances[_from] = creditBalances[_from] - creditAmount;
creditBalances[_to] = creditBalances[_to] + creditAmount;
emit Transfer(_from, _to, _value);
```

This means that the security of the contract is delegated to the checks added by the compiler depending on the pragma used, it must be taken into account that these checks may appear and disappear in future versions of the compiler, so they must be checked at the level of smart contracts.

Affected source code:

  * [Yieldy.sol#L212](https://github.com/code-423n4/2022-06-yieldy/blob/8400e637d9259b7917bde259a5a2fbbeb5946d45/src/contracts/Yieldy.sol#L212)

## Recommendation
* Check that the from account has a `creditAmount` balance.

Looking into this, the balance isn’t calculated through the `creditsForTokenBalance` method, it’s calculated through the `balanceOf` method, which in this case the functionality is correct. We aren’t transferring credits, we are transferring the value and adding to the credits. Allowance is for value amounts, not credits, also balance can only go up against credits, so if the balance is valid then credits are inherently valid too. I’m unsure of what to label this as, because we do need to check to see if the user has the correct balance. I feel like this issue is partially correct.

**[toshiSat (Yieldy) resolved](https://github.com/code-423n4/2022-06-yieldy-findings/issues/36#issuecomment-1199933589):**

<https://github.com/shapeshift/foxy/pull/130/files> for the fix.
