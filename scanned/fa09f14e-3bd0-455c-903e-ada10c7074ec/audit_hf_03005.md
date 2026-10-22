# [H] Frontrunning by malicious validator

## Summary
Severity: High
Contest weight: 0.6020
Dataset id: 16773
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The finding concerns a front‑running vulnerability in the Ethereum 2.0 deposit contract that can be abused by a malicious validator to hijack the withdrawal credentials of a later, legitimate deposit. The contract permits a depositor to provide a public key, a withdrawal credential, a signature and an amount of ether. When a public key is seen for the first time, the supplied withdrawal credential is stored together with the deposit. Subsequent deposits that reference the same public key are allowed – the protocol simply adds the new ether to the validator’s balance and does not verify that the withdrawal credential matches the one already recorded. Because of this design decision, an attacker who can see a pending transaction that intends to register a validator with a 32 ETH deposit can quickly submit a competing deposit using the same public key but only the minimum 1 ETH and a withdrawal credential that points to an address under the attacker’s control. If the attacker’s transaction is mined before the legitimate one, the contract records the attacker’s withdrawal credential. When the protocol later processes the 32 ETH deposit, the balance of the validator is increased as expected, but the withdrawal credential remains the one set by the attacker. Consequently, the attacker can later withdraw the full stake, effectively stealing the funds. The impact is a loss of the staked ether for the protocol or any user that relied on the deposit, as the expected withdrawal address receives nothing and the attacker’s address receives the entire amount. The vulnerability surfaces only when the system allows multiple deposits for the same validator and does not enforce immutability of withdrawal credentials after the first registration. It affects any party that depends on the deposit contract for secure validator onboarding, including protocol operators, delegators and end‑users. The issue was identified during a security audit by analyzing the deposit contract’s logic against the Ethereum consensus specifications, and it is subtle because the contract emits no error and the validator’s balance appears correct, making the malicious credential change easily overlooked. To mitigate the risk, the contract should either forbid any subsequent deposit with a differing withdrawal credential, or explicitly require that the credential supplied in later deposits matches the stored value, effectively making the withdrawal credential immutable after the first successful registration. This would prevent an attacker from overwriting the credential through a front‑run, ensuring that the withdrawal destination remains the one originally intended by the protocol.

## Proof of Concept
A malicious validator can frontrun depositEther transaction for its pubKey and deposit 1 ether for different withdrawal credential, thereby setting withdrawal credit before deposit of 32 ether by contract and thereby when 32 deposit ether are deposited, the withdrawal credential is also what was set before rather than the one being sent in depositEther transaction.

## Recommendation
Set withdrawal credentials for validator by depositing 1 ether with desired withdrawal credentials, before adding it in Operator Registry.

Interesting point, but at the beginning, the only validators we will have will be Frax controlled.


```solidity
function deposit(
    bytes calldata pubkey,
    bytes calldata withdrawal_credentials,
    bytes calldata signature,
    bytes32 deposit_data_root
) override external payable {
    // Extended ABI length checks since dynamic types are used.
    require(pubkey.length == 48, "DepositContract: invalid pubkey length");
    require(withdrawal_credentials.length == 32, "DepositContract: invalid withdrawal_credentials length");
    require(signature.length == 96, "DepositContract: invalid signature length");

    // Check deposit amount
    require(msg.value >= 1 ether, "DepositContract: deposit value too low");
    require(msg.value % 1 gwei == 0, "DepositContract: deposit value not multiple of gwei");
    uint deposit_amount = msg.value / 1 gwei;
    require(deposit_amount <= type(uint64).max, "DepositContract: deposit value too high");

    // Emit `DepositEvent` log
    bytes memory amount = to_little_endian_64(uint64(deposit_amount));
    emit DepositEvent(
        pubkey,
        withdrawal_credentials,
        amount,
        signature,
        to_little_endian_64(uint64(deposit_count))
    );

    // Compute deposit data root (`DepositData` hash tree root)
    bytes32 pubkey_root = sha256(abi.encodePacked(pubkey, bytes16(0)));
    bytes32 signature_root = sha256(abi.encodePacked(
        sha256(abi.encodePacked(signature[:64])),
        sha256(abi.encodePacked(signature[64:], bytes32(0)))
    ));
    bytes32 node = sha256(abi.encodePacked(
        sha256(abi.encodePacked(pubkey_root, withdrawal_credentials)),
        sha256(abi.encodePacked(amount, bytes24(0), signature_root))
    ));

    // Verify computed and expected deposit data roots match
    require(node == deposit_data_root, "DepositContract: reconstructed DepositData does not match supplied deposit_data_root");

    // Avoid overflowing the Merkle tree (and prevent edge case in computing `branch`)
    require(deposit_count < MAX_DEPOSIT_COUNT, "DepositContract: merkle tree full");

    // Add deposit data root to Merkle tree (update a single `branch` node)
    deposit_count += 1;
    uint size = deposit_count;
    for (uint height = 0; height < DEPOSIT_CONTRACT_TREE_DEPTH; height++) {
        if ((size & 1) == 1) {
            branch[height] = node;
            return;
        }
        node = sha256(abi.encodePacked(branch[height], node));
        size /= 2;
    }
    // As the loop should always end prematurely with the `return` statement,
    // this code should be unreachable. We assert `false` just to be safe.
    assert(false);
}
```

It is unclear both in the code above for the deposit contract as well as the documentation on keys

<https://kb.beaconcha.in/ethereum-2.0-depositing>  
<https://kb.beaconcha.in/ethereum-2-keys>

How exactly multiple deposits two the same validator using different withdrawal keys would work. While it would make sense that they would allow a one to many mapping, I am unable to confirm or deny this and therefore will leave the risk currently as High on the side of caution.

Strong find. Indeed in ETH [specs](https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#deposits) we can see that in `process_deposit()`, if the pubkey is already registered, we just increase its balance, not touching the withdrawal_credentials. However the recommended mitigation does not really address the issue IMO, and the detail is quite lacking.

I think it is technically a non-issue because we will be controlling the addition/removal of validators. Should that eventually become open, we will have to look at the entire code from a different perspective to close security holes.

I think it is relevant, because the idea is to make the protocol controlled validators work for the attacker, because they inserted their own withdrawal credentials directly on the deposit contract.

Ohh I see it now. Good point.

More info  
<https://research.lido.fi/t/mitigations-for-deposit-front-running-vulnerability/1239>

Since all of the validators are ours and we have the mnemonic, would it still be an issue though? Lido’s setup is different: <https://medium.com/immunefi/rocketpool-lido-frontrunning-bug-fix-postmortem-e701f26d7971>

<https://github.com/ethereum/consensus-specs/blob/dev/specs/phase0/beacon-chain.md#deposits>  
From @0xJM  
In the scenario that someone frontruns us with a 1 ETH deposit at the same time we do a 32 ETH deposit, their 1 ETH deposit would fail on beaconchain because it would fail bls.Verify. The result would be them losing their 1 ETH.

Our 32 ETH would go through normally and the validator would activate

@FortisFortuna - can you elaborate on why you believe that bls.Verify would fail?

`if not bls.Verify(pubkey, signing_root, deposit.data.signature):`

From @0xJM

<https://github.com/ethereum/staking-deposit-cli/blob/e2a7c942408f7fc446b889097f176238e4a10a76/staking_deposit/credentials.py#L127>

the signing root includes the deposit message which has the withdrawal credentials

<https://github.com/ethereum/staking-deposit-cli/blob/e2a7c942408f7fc446b889097f176238e4a10a76/staking_deposit/credentials.py#L112>

hence bls.Verify would fail on Beaconchain as I mentioned

the consensus spec has that signing _root = compute_ signing _root(deposit_ message, domain) which is verified against the signature.

The signature would be valid. The validator would still sign the message containing the credentials that they are front running with.

From @denett  
“The signature would be valid. The validator would still sign the message containing the credentials that they are front running with.” Only the validator can create a valid signature and we own the key to the validator.

Yea, so this is the root of it, the contest does not specify that Frax is the owner of all validators that are meant to be used with this protocol. Without stating that ahead of time for the Wardens to understand, I believe this to be a valid finding and the warden should be awarded.

Ok. So in our current setup, assuming Frax owns all validators, we are safe?

:) I cannot guarantee anything in DeFi is safe. My understanding of this particular vulnerability is that it would require a validator to act maliciously by using a smaller than 32 ETH deposit to front run your deposit and enable them to control the withdrawal in the future. If the validator is owned by your team and the keys are never exploited, then I don’t see how the front ran signature could be generated.

Ya, I hear you lol. At least for this particular scenario we are ok then, according to the known bug. We can pay out for the bug because none of our team were aware of it and it is good to know for the future.
