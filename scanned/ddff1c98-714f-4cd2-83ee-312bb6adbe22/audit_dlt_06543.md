# [M] Atom wallets can be created and attributed to Triple vaults as well due to invalid validation

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-22
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/32
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** iamandreiski
**Submission hash (on-chain):** 0x73097393c0cbe8c1ed9e3b9df4b12c607b7e2a36218527a734efe18280ae9636
**Severity:** medium

**Description:**
**Description**\
Since there's no validation besides if the atomId isn't 0 or it's not more than the `count`, an Atom wallet can be created/deployed for a Triple vault as well.

**Attack Scenario**\

When deploying a new Atom wallet, according to protocol documentation, as well as Natspec, it should be attributed to an Atom vault. But there's no contract logic preventing a wallet to be deployed for a Triple vault.

When a user wants to deploy an Atom wallet:

```

 function deployAtomWallet(uint256 atomId) external whenNotPaused returns (address) {
        if (atomId == 0 || atomId > count) {
            revert Errors.MultiVault_VaultDoesNotExist();
        }

        // compute salt for create2
        bytes32 salt = bytes32(atomId);

        // get contract deployment data
        bytes memory data = _getDeploymentData();

        address atomWallet;

        // deploy atom wallet with create2:
        // value sent in wei,
        // memory offset of `code` (after first 32 bytes where the length is),
        // length of `code` (first 32 bytes of code),
        // salt for create2
        assembly {
            atomWallet := create2(0, add(data, 0x20), mload(data), salt)
        }

        if (atomWallet == address(0)) {
            revert Errors.MultiVault_DeployAccountFailed();
        }

        return atomWallet;
    }

```

They can pass an Id which is attributed to a Triple vault, since there's no validation to make sure that the Id passed as function argument is not a Triple vault id, the vault will be deployed as usual and attributed to the "Triple vault".

The only logic which validates this is that the vaultId isn't 0 or that it's not more than `count`, since `count` is both incremented for Triple vaults and Atom vaults, this will pass and the wallet will be created.

**Attachments**

1. **Proof of Concept (PoC) File**


2. **Revised Code File (Optional)**
