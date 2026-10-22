# [M] `Vault.mintWithPermit`

## Summary
Severity: Medium
Contest weight: 0.5990
Dataset id: 19017
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the Vault.mintWithPermit function, which combines an ERC20 permit signature with a calculation of the required asset amount based on the number of shares the caller wants to receive. The contract first converts the requested share amount to an asset amount using the current exchange rate, then includes that exact asset amount in the permit call. Because the exchange rate is a mutable value that can change between the moment the off‑chain signature is created and the moment the transaction is mined, an attacker who can front‑run the transaction can alter the vault’s total assets or total shares, causing the exchange rate to shift. When the exchange rate changes, the asset amount derived from the share amount no longer matches the amount that was signed, so the permit call fails and the mintWithPermit transaction reverts. This creates a denial‑of‑service condition: legitimate users who generate a correct signature off‑chain may see their mint attempts repeatedly revert if an adversary repeatedly manipulates the exchange rate, leading to lost gas and an inability to obtain shares. The issue is triggered whenever mintWithPermit is used with a signature that encodes the exact asset amount, i.e., any time a user relies on the current exchange rate to compute the amount before signing. The affected parties are the users of the vault who expect to receive newly minted shares after providing a permit, as well as the protocol that may lose confidence due to blocked minting operations. The problem was discovered during a security audit that examined the flow of permit‑based minting and noticed that the signed amount is not bounded, exposing a race condition between signature generation and execution. The bug is subtle because the transaction only fails when the exchange rate changes, which may not be obvious during normal testing, and the revert message may simply indicate an invalid signature, giving little hint of the underlying front‑running vector. The vulnerability belongs to the class of front‑running or oracle‑manipulation bugs where off‑chain signed data depends on mutable on‑chain state. From a user’s perspective the symptom is a transaction that reverts with a permit‑related error, resulting in no shares being minted and the user’s balance remaining unchanged despite expecting a deposit. To remediate the issue the contract should not sign the exact asset amount; instead it should use an upper‑bound amount in the permit call or employ the ERC20Permit allowance mechanism with a maximum value, allowing the contract to safely pull the required assets after the exchange rate is known, thereby eliminating the race condition.

## Proof of Concept
`Vault.mintWithPermit()` gets the share amount as an input and calculates the asset amount from the share. Then, it approves the asset amount with `permit` method.

```solidity
uint256 _assets = _beforeMint(_shares, _receiver);

_permit(IERC20Permit(asset()), msg.sender, address(this), _assets, _deadline, _v, _r, _s);
_deposit(msg.sender, _receiver, _assets, _shares);
```

The signature is generated using the exact value of the expected asset amount calculated from the share amount, and the resulting asset amount depends on the exchange rate of current vault.

```solidity
function _beforeMint(uint256 _shares, address _receiver) internal view returns (uint256) {
  if (_shares > maxMint(_receiver)) revert MintMoreThanMax(_receiver, _shares, maxMint(_receiver));
  return _convertToAssets(_shares, Math.Rounding.Up);
}

function _convertToAssets(
  uint256 _shares,
  Math.Rounding _rounding
) internal view virtual override returns (uint256) {
  return _convertToAssets(_shares, _currentExchangeRate(), _rounding);
}
```

The resulting asset amount can be different from the value of transaction start time. Even an adversary can front-run and manipulate the exchange rate. If the resulting asset amount is different from the original one, the signature will not work as expected and `mintWithPermit()` will revert in most cases.

## Recommendation
We can input an upper bound of the asset amount instead of the exact value of the asset amount.
