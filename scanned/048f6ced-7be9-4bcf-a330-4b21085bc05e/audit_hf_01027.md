# [M] The Passes ContractInitializationCanBePermanentlyDossed, Forcing Redeployment

## Summary
Severity: Medium
Contest weight: 0.2497
Dataset id: 3889
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Initialization can be dossed by directly creating a rewards vault in the factory. Since CREATE is used to deploy the PassesStakingToken in the initializer of Passes.sol, the potential address of the stakingToken can be calculated based on the Passes.sol contract address and nonce (number of deployed contracts the factory has previously deployed). In this case, the nonce will be 0. See here
The destination address is calculated as the rightmost 20 bytes (160 bits) of the Keccak-256 hash of the rlp encoding of the sender address followed by its nonce. That is: address = keccak256(rlp([sender_address,sender_nonce]))[12:]
As a result, upon contract deployment, before its initialization, an attacker can calculate the address of the PassesStakingToken and then directly call the createRewardsVault in the RewardsVaultFactory.
By calling this, the vault for the staking token is deployed and stored, and subsequent calls to create a rewards vault with the same staking token will fail due to a check in the createRewardsVault function.

Upon initialization front run and stakingToken reward vault deployment, subsequent attempts to deploy the same stakingToken reward vault will always fail causing contract initialization to be dossed.

## Proof of Concept
1. Protocol deploys Passes.sol;

2. The attacker uses the Passes.sol contract address to calculate the potential address of the PassesStakingToken contract;

3. He then front runs the call to initialize Passes.sol, to call the createRewardsVault function in the factory;

4. This creates and sets the vault for the staking token;

5. The protocol’s call to initialize Passes.sol will execute, calling the createRewardsVault function again, which will fail.

6. Initialization is dossed, forcing redeployment.

## Recommendation
Recommend wrapping the createRewardsVault in a try-catch mechanism. If the call fails, catch the error and use the predictRewardsVaultAddress function to set the vault address as polVault.
