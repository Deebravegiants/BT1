# [H] `transferNotionalFrom` doesn’t check `from != to`

## Summary
Severity: High
Contest weight: 0.2649
Dataset id: 958
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function `transferNotionalFrom` of `VaultTracker.sol` uses temporary variables to store the balances. If the “from” and “to” address are the same then the balance of “from” is overwritten by the balance of “to”. This means the balance of “from” and “to” are increased and no balances are decreased, effectively printing money.

Note: `transferNotionalFrom` can be called via `transferVaultNotional` by everyone.

## Proof of Concept
function transferNotionalFrom(address f, address t, uint256 a) external onlyAdmin(admin) returns (bool) {
      Vault memory from = vaults[f];
      Vault memory to = vaults[t];
      ...
      vaults[f] = from;
      ...
      vaults[t] = to;    // if f==t then this will overwrite vaults[f]

function transferVaultNotional(address u, uint256 m, address t, uint256 a) public returns (bool) {
      require(VaultTracker(markets[u][m].vaultAddr).transferNotionalFrom(msg.sender, t, a), 'vault transfer failed');

## Recommendation
Add something like the following: `require (f != t,"Same");`
