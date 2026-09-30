# [H] The first depositor can perform a vault inflation attack on the vaults

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-04
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/79
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xaa998d418c81a4b7485ba8bc4fea1f8c8f7056eb0b05ed7794a3f522d119bce7
**Severity:** high

**Description:**
**Description**\
Vaults are protected from first depositor manipulation attacks by either minting the vault's first tokens to the zero address or by deploying the vault with an initial balance (as it is in this case). If the vault's initial balance at deployment is zero, or the first tokens aren't being minted to the zero address, the vault will be vulnerable to the attack.

```
    function deployVault(
        address vaultTemplate,
        address[] calldata assets,
        uint256[] calldata init_balances,
        uint256[] calldata weights,
        uint256 amp,
        uint256 vaultFee,
        string memory name,
        string memory symbol,
        address chainInterface
    ) override external returns (address) {
```
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystFactory.sol#L65C1-L75C44

**Attack Scenario**\
Here's a good breakdown of the attack scenario by open zeppelin.
> New vaults are at the greatest risk of inflation attacks. Let’s illustrate this with an example: Suppose a user is about to deposit 100 tokens into a new vault as the first depositor. If an attacker front-runs this initial deposit with even 1 wei, this minuscule deposit would still garner the attacker a 100% share of the pool.

Next, the attacker donates an amount greater than or equal to 100 tokens to the vault. This action increases the total balance of the pool, while maintaining the number of shares in circulation.

By the time the initial user’s deposit of 100 tokens makes it to the pool, the calculation for their share ends up being zero due to the way pool shares are calculated with the donated token balance (in this example, 100/101 rounds down to 0).

Finally, the attacker withdraws their share from the pool. Since they are the only one with any shares, this withdrawal equals the balance of the vault. This means the attacker also withdraws the 100 tokens deposited by the initial user, effectively stealing their deposit. 
[full article](https://blog.openzeppelin.com/a-novel-defense-against-erc4626-inflation-attacks)

**Potential fix**
- Mint the vault's first tokens to the zero address 
- When deploying vaults with an initial balance, require that the initial balance is greater than zero. This will ensure that the vault has a sufficient balance to prevent the attack.
