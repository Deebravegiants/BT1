# [M] Withdrawal transactions can get stuck if out-

## Summary
Severity: Medium
Contest weight: 0.3097
Dataset id: 15
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawal transactions may never be executed if the L2 output root for the block,
for which the withdrawal was proven, is challenged and reproposed.
Withdrawal transactions can be reproven in the case that the output root for their
previously proven output index has been updated. This can happen if the L2 output
root was removed by the challenger. However, to circumvent malicious users from
reproving messages all the time and resetting the withdrawal countdown, reproving
can only be done on the same L2 block number (and if the output root changed).
If the challenger deletes the block with the withdrawal transaction and the
proposer proposes a different block that does not have the withdrawal transaction,
the withdrawal transaction can never be finalized - even if a future block includes
the legitimate withdrawal transaction again, as reproving it is bound to the old
provenWithdrawals[withdrawalHash].l2OutputIndex.
Legitimate withdrawal transactions will never be finalized if the proposed block was
challenged and replaced with a different one not having the withdrawal transaction.
As this call fails on the "lowest level", the OptimismPortal, these transactions also
cannot be replayed or be issued refunds. In case the withdrawal transaction was a
token bridge transfer, the tokens are stuck on the other chain and cannot be
recovered by the user.
Optimism L2 block derivation has a long list of validation steps performed on
the validations in a different order than the spec lays out.
There is an error in the order which is described in the spec versus the one in the
implementation.
According to the specs, the following check comes first:
batch.timestamp > batch_origin.time + max_sequencer_drift -> drop:
i.e. a batch that does not adopt the next L1 within time will be
dropped, in favor of an empty batch that can advance the L1
origin. This enforces the max L2 timestamp rule.
After it comes this check:
batch.timestamp < batch_origin.time -> drop: enforce the min L2
timestamp rule.
However, in code in batches.go executes in reverse:
if batch.Batch.Timestamp < batchOrigin.Time {
log.Warn("batch timestamp is less than L1 origin timestamp", "l2_timestamp",
batch.Batch.Timestamp, "l1_timestamp", batchOrigin.Time, "origin",
batchOrigin.ID())
,!
,!
return BatchDrop
}
// If we ran out of sequencer time drift, then we drop the batch and produce an
empty batch instead,
,!
// as the sequencer is not allowed to include anything past this point without
moving to the next epoch.
,!
if max := batchOrigin.Time + cfg.MaxSequencerDrift; batch.Batch.Timestamp > max {
log.Warn("batch exceeded sequencer time drift, sequencer must adopt new L1
origin to include transactions again", "max_time", max)
,!
return BatchDrop
}
In practice this should not lead to any issues because both are drop rules and are
right next to each other.
The code does not align with the ordering laid out in the specification.
Specification of the new base fee calculation is inconsistent with the code.
The "Guaranteed Gas Fee Market" specification provides a pseudocode explaining
how a new base fee is calculated, which has two inconsistencies with the actual
code implementation:
1. When multiple blocks are skipped, the new base fee is applied with a 7/8
reduction per block. The code uses the updated newBaseFee (see
ResourceMetering.sol#L115) while the specification uses the un-updated
prev_basefee.
2. The maximum new base fee in the specification is UINT_64_MAX_VALUE but is
set to type(uint128).max in the code.
The specification does not match the code.
universal/StandardBridge.sol contract do not match the actual code. The
refund logic has been removed since PR#3535.
Specfication error only.
The depositTransaction of OptimismPortal can directly be called by user instead of
intermediate contract. This means from address wont be aliased. But this is not
considered in CrossDomainOwnable contract which plainly undoL1ToL2Alias the
caller
1. Assume depositTransaction is called by User A directly. Since no intermediary
contract so no aliasing is done
2. On L2 side, if _checkOwner is checked
function _checkOwner() internal view override {
require(
owner() == AddressAliasHelper.undoL1ToL2Alias(msg.sender),
"CrossDomainOwnable: caller is not the owner"
);
}
3. This will try undoL1ToL2Alias on User A address and then match with owner
which is incorrect since User A address was never aliased on L1
The owner check might fail for genuine transaction
According to the Withdrawals spec, a block number is one of the submitted inputs
to the OptimismPortal which is not the case.
The documentation says:
"A relayer submits the required inputs to the OptimismPortal contract. The relayer
need not be the same entity which initiated the withdrawal on L2. These inputs
include the withdrawal transaction data, inclusion proofs, and a block number. The
block number must be one for which an L2 output root exists, which commits to the
withdrawal as registered on L2."
In the contract, the _l2OutputIndex is the one used to check for existence of the
outputRoot and not the block number.
function proveWithdrawalTransaction(
Types.WithdrawalTransaction memory _tx,
uint256 _l2OutputIndex,
Types.OutputRootProof calldata _outputRootProof,
bytes[] calldata _withdrawalProof
) external {
// Prevent users from creating a deposit transaction where this address is
the message
,!
// sender on L2. Because this is checked here, we do not need to check
again in
,!
// `finalizeWithdrawalTransaction`.
require(
_tx.target != address(this),
"OptimismPortal: you cannot send messages to the portal contract"
);
// Get the output root and load onto the stack to prevent multiple mloads.
This will
,!
// revert if there is no output root for the given block number.
bytes32 outputRoot = L2_ORACLE.getL2Output(_l2OutputIndex).outputRoot;
// Verify that the output root can be generated with the elements in the
proof.
,!
require(
outputRoot == Hashing.hashOutputRootProof(_outputRootProof),
"OptimismPortal: invalid output root proof"
);
Misleading spec
The specs for system config contains incorrect information and incorrect names for
its contents.
1) The names for overhead and scalar are falsely stated as l1FeeOverhead and
l1FeeScalar in multiple occasions.
2) The list of the configuration update types is missing the unsafe block signer
update
In the SystemConfig contract, there are public variables overhead and scalar:
s/contracts-bedrock/contracts/L1/SystemConfig.sol#L51-L59
Below the variables overhead and scalar are incorrectly named as l1FeeOverhead
and l1FeeScalar in multiple occasions:
m/blob/main/optimism/specs/system_config.md?plain=1#L73
ystem_config.md?plain=1#L86-L90
In the above snippet: Line 89: the names of overhead and scalar It also is missing
the type 3:
• type 3: unsafeBlockSigner overwrite, as address payload.
The corresponding update code snippets from SystemConfig are below:
s/contracts-bedrock/contracts/L1/SystemConfig.sol#L25-L30
s/contracts-bedrock/contracts/L1/SystemConfig.sol#L169-L175
factually incorrect information
• incorrect name of variables
• missing config update type
As the name of variables double as interface to fetch the value, anybody uses the
incorrect name in the specs to fetch the values will fail. Also the specs do not list
the possible config update types, so the users may not know that the
unsafeBlockSigner can be updated.
When creating a contract from L1 (mainnet) to L2 (optimism) the nonce of the
sender is kept at 0 in the context of the transaction receipt and thus the existing
infrastructure (Etherscan) will incorrectly interpret the address of the new contract
(creating a collision).
It is possible to create a contract in Layer 2 from Layer 1 by sending a transaction to
the optimism portal. This is the function of interest:
function depositTransaction(
address _to,
uint256 _value,
uint64 _gasLimit,
bool _isCreation,
bytes memory _data
) public payable metered(_gasLimit)
To create a contract the "_to" address needs to be set to "address(0x0), " the
"_isCreation" needs to be set to "true" and the bytecode needs to be passed in the
"_data" field.
• The contract is then created through the "create" opcode, therefore the
address is computed by hashing the nonce and the address of the sender.
If the nonce is kept at 0 during some time of the execution, the new contract
address will always be the same (nonce is always 0).
is updated), but the receipt displays it wrongly and during a point in the execution
is also kept at 0 so it breaks Etherscan, Blockscout and the rest of the block
exploreres.
Infrastructure tooling like Etherscan is the source of truth for most users, therefore
having inconsistent data between these tools and Optimism is not recommended.
This bug causes existing tooling like Etherscan and Blockscout to display wrong
data in the following ways:
1. The first contract created will always appear as the new contract in contract
creation. See this link for reference: https://goerli-optimism.etherscan.io/addr
ess/0x5d7ee88447367b9212fa655dc863a1e83f7e189d
When the account 0x7d.. creates a new contract from Layer 1, the address "0x5d.."
will always appear as the new contract created.
2. It incorrectly displays contracts as EOA's See this address on etherscan goerli
optimism: https://goerli-optimism.etherscan.io/address/0x0a1c3c13c35275d0
30ff9fb660946cf2fca74ece It appears to be a regular EOA, while in reality, it
is a contract. Run the following command to verify:
cast code 0x0a1c3c13c35275d030ff9fb660946cf2fca74ece --rpc-url
https://goerli.optimism.io
,!
Documentation says that after Bedrock migration all methods interacting with state
on the LegacyERC20 contract will now revert https://github.com/ethereum-optimis
m/optimism/blob/develop/specs/predeploys.md#legacyerc20eth. Functions that
changed state were already reverting and view functions are being updated to still
work.
Just not working as described.
Low
The calculation of sourceHash for L1 attributes deposited is incorrect.
Although, it is a very small difference, because of the misplaced blacket, it means a
different thing with a different result from the actual calculation.
According to the specs, the sourceHash of L1 attributes deposited is calculated
based on:
eposits.md?plain=1#L92
It means the l1BlockHash will be hashed alone, before it is hashed with other
values. However, l1BlockHash and seqNumber should be hashed together, as the
actual calculation in the deposit_source.go:
/rollup/derive/deposit_source.go#L35-L46
Therefore, the line should be corrected as following:
-
`keccak256(bytes32(uint256(1)), keccak256(l1BlockHash),
bytes32(uint256(seqNumber)))`.
,!
+
`keccak256(bytes32(uint256(1)), keccak256(l1BlockHash,
bytes32(uint256(seqNumber))))`.
,!
factually incorrect information
The calculation of sourceHash in the specs will give a different result from the actual
code.
There is no DepositFeed contract. The implementation of Deposit contract would be
OptimismPortal. There are some multiple occasions of incorrect information, for
example, stating that Optimism Portal inherits from DepositFeed contract.
Also, using "Deposit Contract" and DepositFeed contract interchangeably may
confuse the reader.
verview.md?plain=1#L52
There is no DepositFeed contract. It should be OptimismPortal contract.
- The `OptimismPortal` contract emits `TransactionDeposited` events, which the
rollup driver reads in order to process
,!
verview.md?plain=1#L109
Here as well, the DepositFeed contract should be OptimismPortal contract.
call the `depositTransaction` method on the `OptimismPortal` contract. This in
turn emits `TransactionDeposited` events,
,!
verview.md?plain=1#L144
Here as well, the DepositFeed contract should be OptimismPortal contract.
deposits initiated via the `OptimismPortal` contract on L1. All L2 blocks can
also contain _sequenced transactions_, i.e.
,!
thdrawals.md?plain=1#L133-L135
The OptimismPortal inherits Initializable, ResourceMetering and Semver and there
is no DepositFeed contract in the inheritance tree.
Factually wrong specs
Reserve extra slots in the storage layout for future upgrades.
*
A gap size of 41 was chosen here, so that the first slot used in
a child contract
,!
*
would be a multiple of 50.
But actually gap is provided for 42 instead of 41 mentioned above . This can lead to
presumptions on the minds of the dev that the first slot of the child contract is a
multiple of 50 , when it is not .
The process for using the L1CrossDomainMessenger has not been updated in the
spec, and it still explains the pre-Bedrock process rather than the updated process.
The spec explains:
When going from L2 into L1, the user must call relayMessage on the
L1CrossDomainMessenger to finalize the withdrawal. This function can
only be called after the finalization window has passed.
This is no longer the process. In Bedrock:
• the user proves their withdrawal right away
• the user proves their withdrawal on OptimismPortal, not
CrossDomainMessenger
• the user executes their withdrawal on OptimismPortal, not by calling
relayMessage (or any other function) on CrossDomainMessenger
The spec is still showing the old withdrawal process, and doesn't accurately reflect
the new process that will exist in Bedrock.
The withdrawal process in the Introduction of the spec displays the old, single-step
withdrawal process, not the new, two-step one.
The Introduction section of the spec explains withdrawals with the following image:
https://github.com/ethereum-optimism/optimism/blob/develop/specs/assets/user-
withdrawing-to-l1.svg
This image seems to have been drawn for the old withdrawal system, including
steps:
4. Wait for block hash to finalize
5. Send execute withdrawal transaction
In the new system, the user submits the proof right away, then waits at least 7 days
for the proof (regardless of when block hash finalizes), and then makes an
additional call to execute the transaction.
The spec is still showing the old withdrawal process, and doesn't accurately reflect
the new process that will exist in Bedrock.
There is an inconsistency between the spec and the code regarding guarantees for
deposits.
In the spec, it states:
Deposits are guaranteed to be reflected in the L2 state within the
sequencing window.
actually be the case.
Users may expect that there are guarantees in the system that ensure their
deposits will be processed within a given number of blocks, but these guarantees
do not exist yet.
There is an inconsistency between the spec and the code regarding the timing of
L1 block info being submitted to the L2 contract L1Block.sol.
In the spec, it states:
Currently the L1 information is delayed by ten block confirmations (~2.5
minutes) to minimize the impact of reorgs. This value may be reduced in
the future.
However, in the node's derivation code, the L1 block information is included along
with the deposits for each block as it's processed, with no delays.
This can further be verified by watching L1 as well as the L1Block contract, and
observing that, for a given block, the information is posted to Optimism instantly.
• https://goerli.etherscan.io/
• https://goerli-optimism.etherscan.io/address/0x4200000000000000000000
Spec doesn't accurately reflect the reality of what the code is doing.
There is an inconsistency between the spec and reality regarding which user is able
to delete the L2 outputs to roll back the chain.
In the spec, it states:
The proposer may also delete multiple output roots by calling the
deleteL2Outputs() function and specifying the index of the first output to
delete, this will also delete all subsequent outputs.
It goes on to explicitly state that this will be the same role as the sequencer:
proposer will be the same entity as the sequencer, which is a trusted
role. In the future proposers will need to submit a bond in order to post
L2 output roots, and some or all of this bond may be taken in the event of
a faulty proposal.
However, the code specifies a different user, called CHALLENGER, who has this
permission:
require(
msg.sender == CHALLENGER,
"L2OutputOracle: only the challenger address can delete outputs"
);
Looking at the CHALLENGER address, it appears that it is actually a multisig, separate
from both the sequencer and proposer.
The spec is incorrect in defining which user has the ability to roll back the chain.
Wrong description of the withdrawal process in the spec.
The withdrawals.md describes the second step of the withdrawal process as:
2. The OptimismPortal contract retrieves the output root for the given
block number from the L2OutputOracle's getL2OutputAfter()
function, and performs the remainder of the verification process
internally.
The getL2OutputAfter call is never performed. This function does not even exist,
most likely, it was referring to getL2OutputIndexAfter. However, even this function
is not called. What happens in the withdrawal process is that getL2Output is called
to retrieve the output root for the given block number (index).
The withdrawal process should be clearly documented in the spec. Currently, it's
referring to a non-existant function.
Wrong OptimismPortal interface in the specs.
The withdrawals.md specification file shows a wrong L2ToL1MessagePasser
interface:
• function proveWithdrawalTransaction(Types.WithdrawalTransaction memory
_tx, uint256 _l2BlockNumber, Types.OutputRootProof calldata
_outputRootProof, bytes[] calldata _withdrawalProof) external uses the
wrong _l2BlockNumber parameter. The parameter should be named
_l2OutputIndex like in the OptimismPortal code. The difference is that the
L2OutputOracle pushes the blocks to an array, and the startingBlockNumber is
its first element, so there's a shift from a L2 output index to its L2 block
number. Using the block number as described in the spec will make any
proveWithdrawalTransaction calls fail.
interface OptimismPortal {
event WithdrawalFinalized(bytes32 indexed);
function l2Sender() returns(address) external;
function proveWithdrawalTransaction(
Types.WithdrawalTransaction memory _tx,
`_l2OutputIndex`.
,!
Types.OutputRootProof calldata _outputRootProof,
bytes[] calldata _withdrawalProof
) external;
function finalizeWithdrawalTransaction(
Types.WithdrawalTransaction memory _tx
) external;
}
Users usually go to the docs & specification to see how to integrate a project.
Integrating Optimisim's OptimismPortal based on the specification will lead to
errors as it uses the block number, different from the required block index in
L2OutputOracle's array.
Wrong L2ToL1MessagePasser interface in the specs.
The withdrawals.md specification file shows a wrong L2ToL1MessagePasser
interface:
• function nonce() view external returns (uint256); does not exist. It should
be function messageNonce() view external returns (uint256);
interface L2ToL1MessagePasser {
event MessagePassed(
uint256 indexed nonce, // this is a global nonce value for all
withdrawal messages
,!
address indexed sender,
address indexed target,
uint256 value,
uint256 gasLimit,
bytes data,
bytes32 withdrawalHash
);
event WithdrawerBalanceBurnt(uint256 indexed amount);
function burn() external;
function initiateWithdrawal(address _target, uint256 _gasLimit, bytes memory
_data) payable external;
,!
function nonce() view external returns (uint256);
function sentMessages(bytes32) view external returns (bool);
}
Users usually go to the docs & specification to see how to integrate a project.
Integrating Optimisim's L2ToL1MessagePasser based on the specification will lead
to errors.
Wrong L2OutputOracle interface in the specs.
The proposals.md specification file shows a wrong L2OutputOracle interface:
• function getNextBlockNumber() public view returns (uint256) does not
exist. It should be function nextBlockNumber() public view returns
(uint256)
/**
* @notice The number of the first L2 block recorded in this contract.
*/
uint256 public startingBlockNumber;
/**
* @notice The timestamp of the first L2 block recorded in this contract.
*/
uint256 public startingTimestamp;
/**
* @notice Accepts an L2 outputRoot and the timestamp of the corresponding L2
block. The
,!
* timestamp must be equal to the current value returned by `nextTimestamp()` in
order to be
,!
* accepted.
* This function may only be called by the Proposer.
*
* @param _l2Output
The L2 output of the checkpoint block.
* @param _l2BlockNumber The L2 block number that resulted in _l2Output.
* @param _l1Blockhash
A block hash which must be included in the current
chain.
,!
* @param _l1BlockNumber The block number with the specified block hash.
*/
function proposeL2Output(
bytes32 _l2Output,
uint256 _l2BlockNumber,
bytes32 _l1Blockhash,
uint256 _l1BlockNumber
)
/**
* @notice Deletes all output proposals after and including the proposal that
corresponds to
,!
*
the given output index. Only the challenger address can delete
outputs.
,!
*
* @param _l2OutputIndex Index of the first L2 output to be deleted. All outputs
after this
,!
*
output will also be deleted.
*/
function deleteL2Outputs(uint256 _l2OutputIndex) external
/**
* @notice Computes the block number of the next L2 block that needs to be
checkpointed.
,!
*/
function getNextBlockNumber() public view returns (uint256)
Users usually go to the docs & specification to see how to integrate a project.
Integrating Optimisim's L2OutputOracle based on the specification will lead to
errors.
Wrong CrossDomainMessenger interface in the specs.
Vulnerability Details
The messengers.md specification file shows a wrong CrossDomainMessenger
interface:
• function otherMessenger() view external returns (address); does not
exist. It should be function OTHER_MESSENGER() view external returns
(address);
interface CrossDomainMessenger {
event FailedRelayedMessage(bytes32 indexed msgHash);
event RelayedMessage(bytes32 indexed msgHash);
event SentMessage(address indexed target, address sender, bytes message,
uint256 messageNonce, uint256 gasLimit);
,!
function MESSAGE_VERSION() view external returns (uint16);
function messageNonce() view external returns (uint256);
function otherMessenger() view external returns (address);
function failedMessages(bytes32) view external returns (bool);
function relayMessage(uint256 _nonce, address _sender, address _target,
uint256 _value, uint256 _minGasLimit, bytes memory _message) payable
external;
,!
,!
function sendMessage(address _target, bytes memory _message, uint32
_minGasLimit) payable external;
,!
function successfulMessages(bytes32) view external returns (bool);
function xDomainMessageSender() view external returns (address);
}
Users usually go to the docs & specification to see how to integrate a project.
Integrating Optimisim's CrossDomainMessenger based on the specification will
lead to errors.
Wrong Deposited Transaction Type encoding in the specs.
Vulnerability Details
The deposits.md specification file says that the deposited transaction type is
encoded with "the following fields (rlp encoded in the order they appear here)":
However, they are missing the isSystemTransaction bool from the encoding and the
order is also different (data after gasLimit), see:
/**
* @notice RLP encodes the L2 transaction that would be generated when a given
deposit is sent
,!
*
to the L2 system. Useful for searching for a deposit in the L2
system. The
,!
*
*
* @param _tx User deposit transaction to encode.
*
* @return RLP encoded L2 deposit transaction.
*/
function encodeDepositTransaction(Types.UserDepositTransaction memory _tx)
internal
pure
returns (bytes memory)
{
bytes32 source = Hashing.hashDepositSource(_tx.l1BlockHash, _tx.logIndex);
bytes[] memory raw = new bytes[](8);
raw[0] = RLPWriter.writeBytes(abi.encodePacked(source));
raw[1] = RLPWriter.writeAddress(_tx.from);
raw[2] = _tx.isCreation ? RLPWriter.writeBytes("") :
RLPWriter.writeAddress(_tx.to);
,!
raw[3] = RLPWriter.writeUint(_tx.mint);
raw[4] = RLPWriter.writeUint(_tx.value);
raw[5] = RLPWriter.writeUint(uint256(_tx.gasLimit));
raw[6] = RLPWriter.writeBool(false);
raw[7] = RLPWriter.writeBytes(_tx.data);
return abi.encodePacked(uint8(0x7e), RLPWriter.writeList(raw));
}
Users go to the specification to see how to integrate a project. Integrating
according to this spec will be wrong.
Wrong StandardBridge interface in the specs.
Vulnerability Details
The bridges.md specification file shows a wrong StandardBridge interface:
• ERC20BridgeFinalized event is defined twice, this is an invalid interface as
compilation will fail with "DeclarationError: Event with same name and
parameter types defined twice."
• The function parameter _extraData is defined as bytes memory _extraData but
the StandardBridge uses call-data. The encodings are incompatible.
interface StandardBridge {
interface as compilation will fail with "DeclarationError: Event with same
name and parameter types defined twice."
,!
,!
event ERC20BridgeFinalized(address indexed localToken, address indexed
remoteToken, address indexed from, address to, uint256 amount, bytes
extraData);
,!
,!
event ERC20BridgeFinalized(address indexed localToken, address indexed
remoteToken, address indexed from, address to, uint256 amount, bytes
extraData);
,!
,!
event ERC20BridgeInitiated(address indexed localToken, address indexed
remoteToken, address indexed from, address to, uint256 amount, bytes
extraData);
,!
,!
event ETHBridgeFinalized(address indexed from, address indexed to, uint256
amount, bytes extraData);
,!
event ETHBridgeInitiated(address indexed from, address indexed to, uint256
amount, bytes extraData);
,!
function bridgeERC20(address _localToken, address _remoteToken, uint256
_amount, uint32 _minGasLimit, bytes memory _extraData) external;
,!
function bridgeERC20To(address _localToken, address _remoteToken, address
_to, uint256 _amount, uint32 _minGasLimit, bytes memory _extraData) external;
,!
function bridgeETH(uint32 _minGasLimit, bytes memory _extraData) payable
external;
,!
function bridgeETHTo(address _to, uint32 _minGasLimit, bytes memory
_extraData) payable external;
,!
function deposits(address, address) view external returns (uint256);
function finalizeBridgeERC20(address _localToken, address _remoteToken,
address _from, address _to, uint256 _amount, bytes memory _extraData)
external;
,!
,!
function finalizeBridgeETH(address _from, address _to, uint256 _amount,
bytes memory _extraData) payable external;
,!
function messenger() view external returns (address);
function otherBridge() view external returns (address);
}
Users usually go to the docs & specification to see how to integrate a project.
Integrating Optimisim's bridge based on the specification will lead to errors.
Incorrectness in computing block signing hash allows cross-chain replay attacks
The sequencer signs over a message: keccak256(domain ++ chain_id ++
payload_hash). The chain_id is included to prevent replaying the same message
over another chain. However, SigningHash function fails to ensure the chain_id is
included in the message.
func SigningHash(domain [32]byte, chainID *big.Int, payloadBytes []byte)
(common.Hash, error) {
,!
var msgInput [32 + 32 + 32]byte
// domain: first 32 bytes
copy(msgInput[:32], domain[:])
// chain_id: second 32 bytes
if chainID.BitLen() > 256 {
return common.Hash{}, errors.New("chain_id is too large")
}
chainID.FillBytes(msgInput[32:64])
// payload_hash: third 32 bytes, hash of encoded payload
copy(msgInput[32:], crypto.Keccak256(payloadBytes))
return crypto.Keccak256Hash(msgInput[:]), nil
}
If you look at this line:
copy(msgInput[32:], crypto.Keccak256(payloadBytes))
/p2p/signer.go#L36
It is supposed to copy the encoded payload hash to the third 32 bytes of
msgInput. However, it start from 32nd byte which would overwrite the second 32
bytes allocated for the chain_id.
Any block signed by the sequencer in any chain is valid for other chains. For
example, a malicious verifier can pick a message signed for a test chain and gossip
it out for P2P on main chain.
The word "owner" is overloaded and refers to more than one address in the proxies
used in optimism bedrock.
The proxy contract used for several contracts, including L1CrossDomainMessenger,
confuses the meaning of owner in the code and in the spec. In the proxy contract,
there is OWNER_KEY, but this storage slot actually stores the admin of the proxy and
is retrieved by calling admin. This meaning of owner is more confusing because
L1CrossDomainMessenger, the implementation contract behind the proxy, inherits
OwnableUpgradeable and has an owner function, a transferOwnership function, and
an onlyOwner modifier.
The overloading of "owner" makes all documentation with the word "owner"
confusing, and sometimes contradictory, in the specifications and code natspec.
One specific example of this contradiction is from the predeploy spec
ProxyAdmin Address:
0x4200000000000000000000000000000000000018
The ProxyAdmin is the owner of all of the proxy contracts set at the
predeploys. It is itself behind a proxy. The owner of the ProxyAdmin will
have the ability to upgrade any of the other predeploy contracts.
The first time the word "owner" is used, it actually refers to the proxy admin. This is
seen by calling admin on L2CrossDomainMessenger: cast call
0x4200000000000000000000000000000000000007 "admin()(address)" --rpc-url
https://goerli.optimism.io ->
0x4200000000000000000000000000000000000018. Using the same admin
meaning for owner, like the first time the word is used, returns the ProxyAdmin
address, which does not make sense in the context of what the spec is trying to
explain: cast call 0x4200000000000000000000000000000000000018
"admin()(address)" --rpc-url https://goerli.optimism.io ->
0x4200000000000000000000000000000000000018. But the second time the
word "owner" is used, it refers to the owner behind the proxy, in the implementation
contract, which is seen in this cast call: cast call
0x4200000000000000000000000000000000000018 "owner()(address)" --rpc-url
https://goerli.optimism.io ->
0xf80267194936da1E98dB10bcE06F3147D580a62e. This explanation of the spec
should replace the first time the word "owner" is used with the word "admin".
The meaning of owner is ambiguous in many contracts because there owner can
refer to the return value of admin or the return value of owner.
The natspec for changeAdmin and admin in the proxy shows how the word owner is
used to refer to the proxy admin, confusing the two terms
s/contracts-bedrock/contracts/universal/Proxy.sol#L111-L126
The natspec and variable name in L1CrossDomainMessenger uses owner to refer to
a different value
s/contracts-bedrock/contracts/L1/L1CrossDomainMessenger.sol#L38
The predeploy spec for ProxyAdmin summarizes this confusion by using the word
23-01-optimism/blob/main/optimism/specs/predeploys.md#proxyadmin

## Recommendation
Loosen the restriction of reproving: Allow reproving under a new L2 output index
whenever the output root of the proven output index changes. This still balances
the other concern of malicious users reproving transactions to reset the withdrawal
countdown well as in the case where the output root changed, the withdrawal
needs to be proved again anyway to be finalized.
- require(
-
provenWithdrawal.timestamp == 0 ||
-
(_l2OutputIndex == provenWithdrawal.l2OutputIndex &&
-
outputRoot != provenWithdrawal.outputRoot),
-
"OptimismPortal: withdrawal hash has already been proven"
- );
+ require(
+
provenWithdrawal.timestamp == 0 ||
+
L2_ORACLE.getL2Output(provenWithdrawal.l2OutputIndex) !=
provenWithdrawal.outputRoot,
,!
+
"OptimismPortal: withdrawal hash has already been proven"
+ );
Change the code so that it is in line with the specification.
Issue S-2: Specification of the new base fee calculation
is inconsistent with the code
Fix either the specification or the code.
contract
Issue S-4: Incorrect owner check
This check need to be revised. If the transaction came directly from tx.origin
(without any intermediary contract) then no need of removing aliasing
The specification should refer to _l2OutputIndex as one of the inputs instead of
'block number'.
Issue S-6: system_config: incorrect variable name and miss-
ing config update type
Correct the names of the variables and add the missing config update type
Issue S-7: Address collision in cross - chain contract cre-
ation (breaks tooling)
The nonce should be set to the sender's nonce from the op-node.
updated (such as balance using address.balance).
Issue S-9: deposits: the sourceHash of L1 attributes de-
posited
correct the calculation
Issue S-10: overview,withdrawals: DepositFeed does not
exist
Use "Deposit Contract" or OptimismPortal depending on the context, instead of
DepositFeed contract.
Issue S-11: Confusion in gap size
Issue S-12: The CrossDomainMessenger process is ex-
plained incorrectly in the spec
Update the explanation of the CrossDomainMessenger in the spec to explain the
new withdrawal process.
Issue S-13: Withdrawing process in spec does not in-
clude two-step withdrawals
Update the diagram in the spec Introduction to explain the new two-step
withdrawal process.
Issue S-14: Deposits are not guaranteed to be reflected
within sequencing window
Remove this language from the spec until fraud proofs are live.
Remove this language from the spec or adjust the code to match.
Issue S-16: L2OutputOracle outputs are removed by chal-
lenger, not proposer
Adjust the language in the spec to make clear that the CHALLENGER is a separate role
controlled by a multisig.
Issue S-17: Spec: Wrong description of withdrawal pro-
cess
Fix the spec by referring to getL2Output(l2OutputIndex) instead.
Issue S-18: Spec: Wrong OptimismPortal interface
Use the correct interface by fixing the mentioned issues.
Issue S-19: Spec: Wrong L2ToL1MessagePasser interface
Use the correct interface by fixing the mentioned issues.
Issue S-20: Spec: Wrong L2OutputOracle interface
Use the correct interface by fixing the mentioned issues.
Issue S-21: Spec: Wrong CrossDomainMessenger interface
Use the correct interface by fixing the mentioned issues.
Issue S-22: Spec: Wrong Deposited Transaction Type en-
coding
Use the correct encoding from the encodeDepositTransaction function above.
Issue S-23: Spec: Wrong StandardBridge interface
Use the correct interface by fixing the mentioned issues.
Issue S-24: Incorrectness in computing block signing hash
allows cross-chain replay attacks
Just replace this
copy(msgInput[32:], crypto.Keccak256(payloadBytes))
with
copy(msgInput[64:], crypto.Keccak256(payloadBytes))
Run the test above again and it should pass successfully.
Disambiguate the terms admin and owner. The proxyadmin spec explanation should
replace the first time the word "owner" is used with the word "admin". Consider
renaming OWNER_KEY in the proxy contract to ADMIN_KEY and remove the word owner
from the proxy contract.
