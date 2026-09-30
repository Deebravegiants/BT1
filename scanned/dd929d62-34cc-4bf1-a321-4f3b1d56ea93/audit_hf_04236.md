# [H] Attacker can make `0` value `deposit`

## Summary
Severity: High
Contest weight: 0.8463
Dataset id: 21132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119) uses modifier [`isValidDNft()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L42) instead of [`isDNftOwner()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L39), which allows anyone to call [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119) on behalf of any DNft id.

## Proof of Concept
**First impact:**

1. User calls [`redeemDyad()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L184) (or [`withdraw()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L134) to directly withdraw collateral) to burn DYAD and withdraw their collateral asset.
2. Attacker frontruns the call with a `0` value [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119) call. This would set the `idToBlockOfLastDeposit[id]` to the current `block.number`. The call does not revert since `0` value transfers are allowed.

    File: VaultManagerV2.sol
    ```solidity
    function deposit(
      uint    id,
      address vault,
      uint    amount
    ) 
      external 
        isValidDNft(id)
    {
      idToBlockOfLastDeposit[id] = block.number;
      Vault _vault = Vault(vault);
      _vault.asset().safeTransferFrom(msg.sender, address(vault), amount);
      _vault.deposit(id, amount);
    }
    ```

3. When the user’s [`redeemDyad()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L184) call goes through, it internally calls the [`withdraw()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L134) function, which would cause a revert due to the check on Line 152. The check evaluates to true and reverts since the attacker changes the last deposit block number to the current block through the `0` value [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119) call.

    File: VaultManagerV2.sol
    ```solidity
    function withdraw(
      uint    id,
      address vault,
      uint    amount,
      address to
    ) 
      public
        isDNftOwner(id)
    {
      if (idToBlockOfLastDeposit[id] == block.number) revert DepositedInSameBlock();
      uint dyadMinted = dyad.mintedDyad(address(this), id);
      Vault _vault = Vault(vault);
      uint value = amount * _vault.assetPrice() 
                    * 1e18 
                    / 10**_vault.oracle().decimals() 
                    / 10**_vault.asset().decimals();
  
      if (getNonKeroseneValue(id) - value < dyadMinted) revert NotEnoughExoCollat();
      _vault.withdraw(id, to, amount);
      if (collatRatio(id) < MIN_COLLATERIZATION_RATIO)  revert CrTooLow(); 
    }
    ```

4. If the collateral ratio of the user falls below the minimum threshold of 1.5e18 (in terms of high volatility of collateral asset price), the attacker could then exploit the situation to liquidate the user using the [`liquidate()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L205) function.

**Second impact:**

1. User tries to remove a vault by calling the [`remove()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L94) function.
2. Attacker frontruns the call by making a 1 wei collateral deposit through the [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119) function. This would increase the `id2asset` for the user in the vault.

    File: VaultManagerV2.sol
    ```solidity
    function deposit(
      uint    id,
      address vault,
      uint    amount
    ) 
      external 
        isValidDNft(id)
    {
      idToBlockOfLastDeposit[id] = block.number;
      Vault _vault = Vault(vault);
      _vault.asset().safeTransferFrom(msg.sender, address(vault), amount);
      _vault.deposit(id, amount);
    }
    ```

3. User’s call goes through and reverts due to the check on Line 102. This revert occurs since `id2asset` is now 1 wei for the vault the user is trying to remove. Note that although the attacker would be spending gas here, an equal amount of gas would also be required from the user’s side to withdraw the 1 wei. The attack will continue till the user gives up due to the high gas spent behind withdrawing. Another thing to note is that regular users (with no knowledge of contracts) might not have the option to withdraw 1 wei from the frontend, which would require additional overhead from their side to seek help from the team.

    File: VaultManagerV2.sol
    ```solidity
    function remove(
        uint    id,
        address vault
    ) 
      external
        isDNftOwner(id)
    {
      if (Vault(vault).id2asset(id) > 0) revert VaultHasAssets();
      if (!vaults[id].remove(vault))     revert VaultNotAdded();
      emit Removed(id, vault);
    }
    ```

## Recommendation
Use modifier [`isDNftOwner()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L39) instead of [`isValidDNft()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L42) on function [`deposit()`](https://github.com/code-423n4/2024-04-dyad/blob/cd48c684a58158de444b24854ffd8f07d046c31b/src/core/VaultManagerV2.sol#L119).
