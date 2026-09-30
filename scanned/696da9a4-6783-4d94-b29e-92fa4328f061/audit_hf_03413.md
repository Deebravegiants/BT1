# [M] `migratePartnerVault`

## Summary
Severity: Medium
Contest weight: 0.2779
Dataset id: 18615
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract contains a logical validation error in the migratePartnerVault function. The function is intended to replace the current partner vault with a new one, but it first checks whether the supplied vault address is recognised by calling factory.vaultIds(newVault) and rejecting the call if the returned identifier equals zero. The developers also use the identifier value zero as a sentinel that represents an illegal or uninitialised vault address. However, the factory that stores vault identifiers assigns identifiers starting at zero because the vault array is populated without a placeholder entry for address(0). Consequently, the very first vault that is added to the system receives the identifier 0, which is indistinguishable from the sentinel value used to flag an illegal vault. When an owner attempts to migrate to this first vault, the check incorrectly interprets the identifier as unrecognised and reverts with UnrecognizedVault, preventing the migration. This bug manifests whenever the first vault – the one with index zero – is the target of a migration, effectively locking the contract out of upgrading to that vault. From a user perspective the partner vault address remains unchanged, any expected balance transfers or claimOutstanding calls are never executed, and the UI may show that a migration request failed without a clear reason. The impact is a denial‑of‑service condition for the contract owner: they cannot move to the first vault, which may hold funds or be required for future upgrades, potentially leaving assets inaccessible or the protocol unable to evolve. The issue was discovered during a manual audit that compared the migration logic with the factory’s addVault implementation and noticed the mismatch between the sentinel usage and the zero‑based indexing. The problem is subtle because zero is a common default value in Solidity and developers often rely on it as a “null” indicator, making the bug easy to overlook in code reviews. To remediate, the factory should reserve the zero index for a dummy entry (e.g., push address(0) into the vault array during construction) or the migration function should use a different sentinel such as checking for address(0) directly, or compare against a mapping that distinguishes between “not present” and a legitimate identifier (for example by using a separate boolean flag or by starting identifiers at 1). In essence, the contract must avoid conflating a valid identifier with a sentinel value, thereby restoring the ability to migrate to any legitimate vault, including the first one, and eliminating the denial‑of‑service risk.

## Proof of Concept
In the `migratePartnerVault()` method, it will determine whether `newPartnerVault` is legal or not, by `vaultId!=0` of the vault.

The code is as follows:
    
    function migratePartnerVault(address newPartnerVault) external onlyOwner {
        if (factory.vaultIds(IBaseVault(newPartnerVault)) == 0) revert UnrecognizedVault();
    
        address oldPartnerVault = partnerVault;
        if (oldPartnerVault != address(0)) IBaseVault(oldPartnerVault).clearAll();
        bHermesToken.claimOutstanding();

But when `factory` adds to the vault, the index starts from 0, so the Id of the first vault is 0,

`PartnerManagerFactory.addVault()`:
    
    contract PartnerManagerFactory is Ownable, IPartnerManagerFactory {
        constructor(ERC20 _bHermes, address _owner) {
            _initializeOwner(_owner);
            bHermes = _bHermes;
            partners.push(PartnerManager(address(0)));
        }
    
        function addVault(IBaseVault newVault) external onlyOwner {
            uint256 id = vaults.length;
            vaults.push(newVault);
            vaultIds[newVault] == id;
    
            emit AddedVault(newVault, id);
        }

The id of the first vault starts from `0`, because in the `constructor`, it does not add `address(0)` to the vaults, similar to `partners`.

So `migratePartnerVault()` can’t be processed for the first vault.

## Recommendation
Similar to `partners`, in the `constructor` method, a vault with `address(0)` is added by default.
    
    contract PartnerManagerFactory is Ownable, IPartnerManagerFactory {
        constructor(ERC20 _bHermes, address _owner) {
            _initializeOwner(_owner);
            bHermes = _bHermes;
            partners.push(PartnerManager(address(0)));
            vaults.push(IBaseVault(address(0)));
        }
