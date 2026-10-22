# [H] Fee Precision Loss Disrupts Liquidity and Liquidations

## Summary
Severity: High
Contest weight: 0.7936
Dataset id: 23151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Borrowing and funding fees of both longs/shorts suffer from two distinct sources of precision loss. The level of precision loss is large enough to consistently occur at a significant level, and can even result in total omission of fee payment for periods of time. This error is especially disruptive given the sensitive nature of funding fee calculations both in determining liquidations (a core functionality), as well as payments received by LPs and funding recipients (representing a significant loss).

The first of the aforementioned sources of precision loss is relating to the DENOM parameter defined and used in apply of math.vy:
This function is in turn referenced (to extract the fee parameter in particular) in several locations throughout fees.vy, namely in determining the funding and borrowing payments made by positions open for a duration of time:
fee one wants to support and the blocktime.” In fact, given its current value of 10−9, the smallest representable fee per block is 10−7%. Given the average blocktimes of 2.0 sec on the BOB chain, there are 15_778_800 blocks in a standard calendar year. Combined with the fee per block, this translates to an annual fee of 1.578%.

However, this is also the interval size for annualized fees under the current system. As a result, any fee falling below the next interval will be rounded down. For example, given an annualized funding rate in the neighborhood of 15%, there is potential for a nearly 10% error in the interest rate if rounding occurs just before the next interval. This error is magnified the smaller the funding rates become. An annual fee of 3.1% would round down to 1.578%, representing an error of nearly 50%. And any annualized fees below 1.578% will not be recorded, representing a 100% error.

The second source of precision loss combines with the aforementioned error, to both increase the severity and frequency of error. It's related to how percentages are handled in params.vy, particularly when the long/short utilization is calculated to determine funding & borrow rates. The utilization is shown below:
This function is in turn used to calculate borrowing (and funding rates, following a slightly different approach that similarly combines the use of utilization and scale), in utilization will have just 2 digits of precision, resulting from the division of reserves by 100. However, this approach can similarly lead to fee rates losing a full percentage point in their absolute value. Since the utilization is used by dynamic_fees to calculate the funding / borrow rates, when combined with the formerly described source of precision loss the error is greatly amplified.

Consider a scenario when the long open interest is 199_999 * 1018 and the reserves are 10_000_000 * 1018. Under the current utilization functionality, the result would be a 1.9999% utilization rounded down to 1%. Further assuming the value of max_fee = 65 (this represents a 100% annual rate and 0.19% 8-hour rate), the long borrow rate would round down to 0%. Had the 1.9999% utilization rate not been rounded down 1%, the result would have been r = 1.3. In turn, the precision loss in DENOM would have effectively rounded down to r = 1, resulting in a 2.051% borrow rate rounded down to 1.578%.

In other words, the precision loss in DENOM alone would have resulted in a 23% error in this case. But when combined with the precision loss in percentage points represented in utilization, a 100% error resulted. While the utilization and resulting interest rates will typically not be low enough to produce such drastic errors, this hopefully illustrates the synergistic combined impact of both sources of precision loss. Even at higher, more representative values for these rates (such as r = 10), errors in fee calculations exceeding 10% will consistently occur.

All fees in the system will consistently be underpaid by a significant margin, across all pools and positions. Additionally trust/confidence in the system will be eroded as fee application will be unpredictable, with sharp discontinuities in rates even given moderate changes in pool utilization. Finally, positions will be subsidized at the expense of LPs, since the underpayment of fees will make liquidations less likely and take longer to occur.

As a result, LPs and funding recipients will have lesser incentive to provide liquidity, as they are consistently being underpaid while taking on a greater counterparty risk.

As an example, consider the scenario where the long open interest is 1_099_999 * 1018 and the reserves are 10_000_000 * 1018. Under the current utilization functionality, the result would be a 10.9999% utilization rounded down to 10%. Assuming max_fee = 65 (100% annually, 0.19% 8-hour), the long borrow rate would be r = 6.5 rounded down to r = 6. A 9.5% annual rate results, whereas the accurate result if neither precision loss occurred is r = 7.15 or 11.3% annually. The resulting error in the borrow rate is 16%.

Assuming a long collateral of 100_000 * 1018, LPs would earn 9_500 * 1018, when they should earn 11_300 * 1018, a shortfall of 1_800 * 1018 from longs alone. Additional borrow fee shortfalls would occur for shorts, in addition to shortfalls in funding payments received.

Liquidation from borrow rates alone should have taken 106 months based on the expected result of 11.3% per annum. However, under the 9.5% annual rate it would take 127 months to liquidate a position. This represents a 20% delay in liquidation time from borrow rates alone, not including the further delay caused by potential underpaid funding rates.

When PnL is further taken into account, these delays could mark the difference between a period of volatility wiping out a position. As a result, these losing positions could run for far longer than should otherwise occur and could even turn into winners. Not only are LP funds locked for longer as a result, they are at a greater risk of losing capital to their counterparty. On top of this, they are also not paid their rightful share of profits, losing out on funds to take on an unfavorably elevated risk.

Thus, not only do consistent, material losses (significant fee underpayment) occur but a critical, core functionality malfunctions (liquidations are delayed).

In the included PoC, three distinct tests demonstrate the individual sources of precision loss, as well as their combined effect. Similar scenarios were demonstrated as discussed above, for example interest = 199_999 * $10^{18}$ with reserves = 10_000_000 * 1018 with a max fee of 65.

The smart contracts were stripped to isolate the relevant logic, and foundry was used for testing. To run the test, clone the repo and place Denom.vy in vyper_contracts, and place Denom.t.sol, Cheat.sol, and IDenom.sol under src/test.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;
import {CheatCodes} from "./Cheat.sol";
import "../../lib/ds-test/test.sol";
import "../../lib/utils/Console.sol";
import "../../lib/utils/VyperDeployer.sol";
import "../IDenom.sol";

contract DenomTest is DSTest {
    VyperDeployer vyperDeployer = new VyperDeployer();
    CheatCodes vm = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    IDenom denom;

    uint256 constant YEAR = (60*60*24*(365) + 60*60*24 / 4); //includes leap year

    function setUp() public {
        vm.roll(1);
        denom = IDenom(vyperDeployer.deployContract("Denom"));
    }

    function testDenom() public {
        uint256 blocksInYr = (YEAR) / 2;
        vm.roll(blocksInYr);
        denom.update();
        // pools were initialized at block 0
        denom.calc(true, 1e25, 0);
        denom.calc2(true, 1e25, 0);
    }

    function testRounding() public {
        uint max_fee = 100; // set max 8-hour rate to 0.288% (157.8% annually)
        uint256 reserves = 10_000_000 ether;
        uint256 interest1 = 1_000_000 ether;
        uint256 interest2 = 1_099_999 ether;
        uint256 util1 = denom.utilization(reserves, interest1);
        uint256 util2 = denom.utilization(reserves, interest2);
        assertEq(util1, util2); // current calculation yields same utilization for both interests

        // borrow rate
        uint fee1 = denom.scale(max_fee, util1);
        uint fee2 = denom.scale(max_fee, util2);
        assertEq(fee1, fee2); // results in the same fee also. fee2 should be ~1% higher
    }

    function testCombined() public {
        // now let's see what would happen if we raised the precision of both fees and percents
        uint max_fee = 65;
        uint max_fee2 = 65_000; // 3 extra digits of precision lowers error by 3 orders of magnitude

        uint256 reserves = 10_000_000 ether;
        uint256 interest = 199_999 ether; // interest & reserves same in both, only differ in precision.

        uint256 util1 = denom.utilization(reserves, interest);
        uint256 util2 = denom.utilization2(reserves, interest); // 3 extra digits of precision here also

        // borrow rate
        uint fee1 = denom.scale(max_fee, util1);
        uint fee2 = denom.scale2(max_fee2, util2);
        assertEq(fee1 * 1_000, fee2 - 999); // fee 1 is 1.000, fee 2 is 1.999 (~50% error)
    }
}

// Possible caller modes for readCallers()
enum CallerMode {
    None,
    Broadcast,
    RecurrentBroadcast,
    Prank,
    RecurrentPrank
}

enum AccountAccessKind {
    Call,
    DelegateCall,
    CallCode,
    StaticCall,
    Create,
    SelfDestruct,
    Resume
}

struct Wallet {
    address addr;
    uint256 publicKeyX;
    uint256 publicKeyY;
    uint256 privateKey;
}

struct ChainInfo {
    uint256 forkId;
    uint256 chainId;
}

struct AccountAccess {
    ChainInfo chainInfo;
    AccountAccessKind kind;
    address account;
    address accessor;
    bool initialized;
    uint256 oldBalance;
    uint256 newBalance;
    bytes deployedCode;
    uint256 value;
    bytes data;
    bool reverted;
    StorageAccess[] storageAccesses;
}

struct StorageAccess {
    address account;
    bytes32 slot;
    bool isWrite;
    bytes32 previousValue;
    bytes32 newValue;
    bool reverted;
}

// Derives a private key from the name, labels the account with that name, and returns the wallet
function createWallet(string calldata) external returns (Wallet memory);

// Generates a wallet from the private key and returns the wallet
function createWallet(uint256) external returns (Wallet memory);

// Generates a wallet from the private key, labels the account with that name, and returns the wallet
function createWallet(uint256, string calldata) external returns (Wallet memory);

// Signs data, (Wallet, digest) => (v, r, s)
function sign(Wallet calldata, bytes32) external returns (uint8, bytes32, bytes32);

// Get nonce for a Wallet
function getNonce(Wallet calldata) external returns (uint64);

// Set block.timestamp
function warp(uint256) external;

// Set block.number
function roll(uint256) external;

// Set block.basefee
function fee(uint256) external;

// Set block.difficulty
// Does not work from the Paris hard fork and onwards, and will revert instead.
function difficulty(uint256) external;

// Set block.prevrandao
// Does not work before the Paris hard fork, and will revert instead.
function prevrandao(bytes32) external;

// Set block.chainid
function chainId(uint256) external;

// Loads a storage slot from an address
function load(address account, bytes32 slot) external returns (bytes32);

// Stores a value to an address' storage slot
function store(address account, bytes32 slot, bytes32 value) external;

// Signs data
function sign(uint256 privateKey, bytes32 digest) external returns (uint8 v, bytes32 r, bytes32 s);

// Computes address for a given private key
function addr(uint256 privateKey) external returns (address);

// Derive a private key from a provided mnemonic string,
// or mnemonic file path, at the derivation path m/44'/60'/0'/0/{index}.
function deriveKey(string calldata, uint32) external returns (uint256);

// Derive a private key from a provided mnemonic string, or mnemonic file path,
// at the derivation path {path}{index}
function deriveKey(string calldata, string calldata, uint32) external returns (uint256);

// Gets the nonce of an account
function getNonce(address account) external returns (uint64);

// Sets the nonce of an account
// The new nonce must be higher than the current nonce of the account
function setNonce(address account, uint64 nonce) external;

// Performs a foreign function call via terminal
function ffi(string[] calldata) external returns (bytes memory);

// Set environment variables, (name, value)
function setEnv(string calldata, string calldata) external;

// Read environment variables, (name) => (value)
function envBool(string calldata) external returns (bool);
function envUint(string calldata) external returns (uint256);
function envInt(string calldata) external returns (int256);
function envAddress(string calldata) external returns (address);
function envBytes32(string calldata) external returns (bytes32);
function envString(string calldata) external returns (string memory);
function envBytes(string calldata) external returns (bytes memory);

// Read environment variables as arrays, (name, delim) => (value[])
function envBool(string calldata, string calldata) external returns (bool[] memory);
function envUint(string calldata, string calldata) external returns (uint256[] memory);
function envInt(string calldata, string calldata) external returns (int256[] memory);
function envAddress(string calldata, string calldata) external returns (address[] memory);
function envBytes32(string calldata, string calldata) external returns (bytes32[] memory);
function envString(string calldata, string calldata) external returns (string[] memory);
function envBytes(string calldata, string calldata) external returns (bytes[] memory);

// Read environment variables with default value, (name, value) => (value)
function envOr(string calldata, bool) external returns (bool);
function envOr(string calldata, uint256) external returns (uint256);
function envOr(string calldata, int256) external returns (int256);
function envOr(string calldata, address) external returns (address);
function envOr(string calldata, bytes32) external returns (bytes32);
function envOr(string calldata, string calldata) external returns (string memory);
function envOr(string calldata, bytes calldata) external returns (bytes memory);

// Read environment variables as arrays with default value, (name, value[]) => (value[])
function envOr(string calldata, string calldata, bool[] calldata) external returns (bool[] memory);
function envOr(string calldata, string calldata, uint256[] calldata) external returns (uint256[] memory);
function envOr(string calldata, string calldata, int256[] calldata) external returns (int256[] memory);
function envOr(string calldata, string calldata, address[] calldata) external returns (address[] memory);
function envOr(string calldata, string calldata, bytes32[] calldata) external returns (bytes32[] memory);
function envOr(string calldata, string calldata, string[] calldata) external returns (string[] memory);
function envOr(string calldata, string calldata, bytes[] calldata) external returns (bytes[] memory);

// Convert Solidity types to strings
function toString(address) external returns(string memory);
function toString(bytes calldata) external returns(string memory);
function toString(bytes32) external returns(string memory);
function toString(bool) external returns(string memory);
function toString(uint256) external returns(string memory);
function toString(int256) external returns(string memory);

// Sets the *next* call's msg.sender to be the input address
function prank(address) external;

// Sets all subsequent calls' msg.sender to be the input address until `stopPrank` is called
function startPrank(address) external;

// Sets the *next* call's msg.sender to be the input address, and the tx.origin to be the second input
function prank(address, address) external;

// Sets all subsequent calls' msg.sender to be the input address until `stopPrank` is called, and the tx.origin to be the second input
function startPrank(address, address) external;

// Resets subsequent calls' msg.sender to be `address(this)`
function stopPrank() external;

// Reads the current `msg.sender` and `tx.origin` from state and reports if there is any active caller modification
function readCallers() external returns (CallerMode callerMode, address msgSender, address txOrigin);

// Sets an address' balance
function deal(address who, uint256 newBalance) external;

// Sets an address' code
function etch(address who, bytes calldata code) external;

// Marks a test as skipped. Must be called at the top of the test.
function skip(bool skip) external;

// Expects an error on next call
function expectRevert() external;
function expectRevert(bytes calldata) external;
function expectRevert(bytes4) external;

// Record all storage reads and writes
function record() external;

// Gets all accessed reads and write slot from a recording session, for a given address
function accesses(address) external returns (bytes32[] memory reads, bytes32[] memory writes);

// Record all account accesses as part of CREATE, CALL or SELFDESTRUCT opcodes in order,
// along with the context of the calls.
function startStateDiffRecording() external;

// Returns an ordered array of all account accesses from a `startStateDiffRecording` session.
function stopAndReturnStateDiff() external returns (AccountAccess[] memory accesses);

// Record all the transaction logs
function recordLogs() external;

// Gets all the recorded logs
function getRecordedLogs() external returns (Log[] memory);

// Prepare an expected log with the signature:
//
// (bool checkTopic1, bool checkTopic2, bool checkTopic3, bool checkData).
//
// Call this function, then emit an event, then call a function.
// Internally after the call, we check if logs were emitted in the expected order with the expected topics and data (as specified by the booleans)
//
// The second form also checks supplied address against emitting contract.
function expectEmit(bool, bool, bool, bool) external;
function expectEmit(bool, bool, bool, bool, address) external;

// Mocks a call to an address, returning specified data.
//
// Calldata can either be strict or a partial match, e.g. if you only
// pass a Solidity selector to the expected calldata, then the entire Solidity function will be mocked.
function mockCall(address, bytes calldata, bytes calldata) external;

// Reverts a call to an address, returning the specified error
//
// Calldata can either be strict or a partial match, e.g. if you only
// pass a Solidity selector to the expected calldata, then the entire Solidity function will be mocked.
function mockCallRevert(address where, bytes calldata data, bytes calldata retdata) external;

// Clears all mocked and reverted mocked calls
function clearMockedCalls() external;

// Expect a call to an address with the specified calldata.
// Calldata can either be strict or a partial match
function expectCall(address callee, bytes calldata data) external;

// Expect a call to an address with the specified calldata and message value.
// Calldata can either be strict or a partial match
function expectCall(address callee, uint256, bytes calldata data) external;

// Gets the _creation_ bytecode from an artifact file. Takes in the relative path to the json file
function getCode(string calldata) external returns (bytes memory);

// Gets the _deployed_ bytecode from an artifact file. Takes in the relative path to the json file
function getDeployedCode(string calldata) external returns (bytes memory);

// Label an address in test traces
function label(address addr, string calldata label) external;

// Retrieve the label of an address
function getLabel(address addr) external returns (string memory);

// When fuzzing, generate new inputs if conditional not met
function assume(bool) external;

// Set block.coinbase (who)
function coinbase(address) external;

// Using the address that calls the test contract or the address provided as the sender, has the next call (at this call depth only) create a transaction that can later be signed and sent onchain
function broadcast() external;
function broadcast(address) external;

// Using the address that calls the test contract or the address provided as the sender, has all subsequent calls (at this call depth only) create transactions that can later be signed and sent onchain
function startBroadcast() external;
function startBroadcast(address) external;
function startBroadcast(uint256 privateKey) external;

// Stops collecting onchain transactions
function stopBroadcast() external;

// Reads the entire content of file to string, (path) => (data)
function readFile(string calldata) external returns (string memory);

// Get the path of the current project root
function projectRoot() external returns (string memory);

// Reads next line of file to string, (path) => (line)
function readLine(string calldata) external returns (string memory);

// Writes data to file, creating a file if it does not exist, and entirely replacing its contents if it does.
// (path, data) => ()
function writeFile(string calldata, string calldata) external;

// Writes line to file, creating a file if it does not exist.
// (path, data) => ()
function writeLine(string calldata, string calldata) external;

// Closes file for reading, resetting the offset and allowing to read it from beginning with readLine.
// (path) => ()
function closeFile(string calldata) external;

// Removes file. This cheatcode will revert in the following situations, but is not limited to just these cases:
// - Path points to a directory.
// - The file doesn't exist.
// - The user lacks permissions to remove the file.
// (path) => ()
function removeFile(string calldata) external;

// Returns true if the given path points to an existing entity, else returns false
// (path) => (bool)
function exists(string calldata) external returns (bool);

// Returns true if the path exists on disk and is pointing at a regular file, else returns false
// (path) => (bool)
function isFile(string calldata) external returns (bool);

// Returns true if the path exists on disk and is pointing at a directory, else returns false
// (path) => (bool)
function isDir(string calldata) external returns (bool);

// Return the value(s) that correspond to 'key'
function parseJson(string memory json, string memory key) external returns (bytes memory);

// Return the entire json file
function parseJson(string memory json) external returns (bytes memory);

// Check if a key exists in a json string
function keyExists(string memory json, string memory key) external returns (bytes memory);

// Get list of keys in a json string
function parseJsonKeys(string memory json, string memory key) external returns (string[] memory);

// Snapshot the current state of the evm.
// Returns the id of the snapshot that was created.
// To revert a snapshot use `revertTo`
function snapshot() external returns (uint256);

// Revert the state of the evm to a previous snapshot
// Takes the snapshot id to revert to.
// This deletes the snapshot and all snapshots taken after the given snapshot id.
function revertTo(uint256) external returns (bool);

// Creates a new fork with the given endpoint and block,
// and returns the identifier of the fork
function createFork(string calldata, uint256) external returns (uint256);

// Creates a new fork with the given endpoint and the _latest_ block,
// and returns the identifier of the fork
function createFork(string calldata) external returns (uint256);

// Creates _and_ also selects a new fork with the given endpoint and block,
// and returns the identifier of the fork
function createSelectFork(string calldata, uint256) external returns (uint256);

// Creates _and_ also selects a new fork with the given endpoint and the latest block and returns the identifier of the fork
function createSelectFork(string calldata) external returns (uint256);

// Takes a fork identifier created by `createFork` and sets the corresponding forked state as active.
function selectFork(uint256) external;

// Returns the currently active fork
// Reverts if no fork is currently active
function activeFork() external returns (uint256);

// Updates the currently active fork to given block number
// This is similar to `roll` but for the currently active fork
function rollFork(uint256) external;

// Updates the given fork to given block number
function rollFork(uint256 forkId, uint256 blockNumber) external;

// Fetches the given transaction from the active fork and executes it on the current state
function transact(bytes32) external;

// Fetches the given transaction from the given fork and executes it on the current state
function transact(uint256, bytes32) external;

// Marks that the account(s) should use persistent storage across fork swaps in a multifork setup, meaning, changes made to the state of this account will be kept when switching forks
function makePersistent(address) external;
function makePersistent(address, address) external;
function makePersistent(address, address, address) external;
function makePersistent(address[] calldata) external;

// Revokes persistent status from the address, previously added via `makePersistent`
function revokePersistent(address) external;
function revokePersistent(address[] calldata) external;

// Returns true if the account is marked as persistent
function isPersistent(address) external returns (bool);

/// Returns the RPC url for the given alias
function rpcUrl(string calldata) external returns (string memory);

/// Returns all rpc urls and their aliases `[alias, url][]`
function rpcUrls() external returns (string[2][] memory);
```

```solidity
// SPDX-License-Identifier: MIT
pragma solidity >=0.8.13;
interface IDenom {
    function update() external;
    function calc(bool, uint256, uint256) external returns(SumFees memory);
    function calc2(bool, uint256, uint256) external returns(SumFees memory);
    function utilization(uint256, uint256) external returns(uint256);
    function utilization2(uint256, uint256) external returns(uint256);
    function scale(uint256, uint256) external returns(uint256);
    function scale2(uint256, uint256) external returns(uint256);

    struct SumFees{
        uint256 funding_paid;
        uint256 funding_received;
    }
}
```

## Recommendation
Consider increasing the precision of DENOM by atleast 3 digits, i.e. DENOM: constant(uint256) = 1_000_000_000_000 instead of 1_000_000_000. Consider increasing the precision of percentages by 3 digits, i.e. divide / multiply by 100_000 instead of 100. Each added digit of precision decreases the precision loss by an order of magnitude. In other words the 1% and 1.5% absolute errors in precision would shrink to 0.01% and 0.015% when using three extra digits of precision.
Consult Denom.vy for further guidance on necessary adjustments to make to the various functions to account for these updated values.
