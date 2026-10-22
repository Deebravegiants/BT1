# [M] Not cleaning upper bits of certain data could

## Summary
Severity: Medium
Contest weight: 0.5944
Dataset id: 22853
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lack of cleaning upper bits of certain variables might lead to setting incorrect values in the protocol, leading to improper behavior of the contract. All values in the EVM are stored as 256 bit values. When a value with a type smaller than 256 bits is used, it is necessary to clean the remaining bits. This is performed by the Solidity compiler by default. However, in yul this cleaning is not performed, so values need to be cleaned manually. However, the Telcoin Wallet implementation lacks performing such data cleaning, which makes the wallet susceptible of accepting incorrect data as valid. This step is extremely important, as it can lead to unexpected outcomes if data is not properly formatted. owners/gatekeepers are trusted, it is easy to leave dirty bits that might affect the code. For example, expressions of type address(uint160(packed)) that aim at converting packed data to an address will leave dirty upper bits. This could lead to several consequences affecting the wallet, as it is unknown how interaction with this wallets will be performed, and nothing guarantees that calldata passed to it will be 100% clean. The following situations could arise due to not cleaning dirty upper bits:
• Making the wallet be locked forever. In the situation where there are no owners in the wallet and only the two gatekeepers have access to it, the gatekeepers could decide to change one of the gatekeeper’s address in order to add a different gatekeeper. This can be done via the replaceGatekeeper function:
```solidity
function replaceGatekeeper() {
    let _old := calldataload(0x4)
    upper bits of certain data could lead to wallet being unaccessible forever
    sstore(_old, 0) // Delete the old mapping.
    sstore(_new, 3) // Add the new mapping.
    stop()
}
```
This could lead to a critical situation where if the _old address is passed without dirty upper bits but the _new address is passed with actual dirty upper bits (maybe due to a different way of fetching both addresses when interacting with the wallet and building the calldata), a wrong _new address would be set as the gatekeeper. This would make the wallet remain locked forever, given that the addOwner and replaceGatekeeper functions in the wallet are expected to be triggered via execute, which requires at least two signers. In this situation, because one of the gatekeepers has been improperly updated due to dirty upper bits, the wallet will remain locked forever, leading to unrecoverable stuck funds. This could also happen when adding an incorrect owner (although the impact would be smaller). When triggering the addOwner function, the _owner is directly extracted from calldata and stored to storage. If _owner contains dirty upper bits, an incorrect value will be set as the owner of the wallet:
```solidity
// TelcoinWallet.sol
function addOwner() {
    let _owner := calldataload(0x4)
}
```
• Transactions failing. The execute function will trigger the internal __ecrecover function so that the signer’s address can be recovered from a signature:
```solidity
function __ecrecover(h, v, r, s) -> a {
    // The builtin ecrecover() function is stored in a builtin contract deployed at
    // address 0x1, with a gas cost hard-coded to 3000 Gas. It expects to be passed
    // exactly 4 words:
    // (offset 0x00) keccak256 hash of the signed data
    // (offset 0x20) v value of the ECDSA signature, with v==27 or v==28
    // (offset 0x40) r value of the ECDSA signature
    // (offset 0x60) s value of the ECDSA signature
    // Since we will receive signatures with v values of 0 or 1, we can unconditionally
    // add 27 to transform them into the format expected by ecrecover().
    v := add(v, 27)
    mstore(0, h)
    mstore(0x20, v)
    mstore(0x40, r)
    mstore(0x60, s)
    // Instead of sending 3000 == 0x0bb8 Gas, we will send a little more with
    // since this will have the same result and save us some Gas when deploying the
    // contract (0x00 bytes are cheaper to deploy).
    if iszero(staticcall(0x0c00, 0x1, 0, 0x80, 0, 0x20)) {
        revert(0, 0)
    }
    a := mload(0)
}
```
Although the r and s values are 32-byte values, v consists of only 1 byte. This makes it susceptible of containing dirty upper bits, which could lead to valid signed transactions failing due to an incorrect value of v containing garbage in the top bits.
• Storage clashing: Telcoin Wallet uses the beacon proxy pattern, where the ClonableBeaconProxy inherits from Initializable, a contract that helps preventing the initialize function from being called more than once:
```solidity
// ClonableBeaconProxy.sol
contract ClonableBeaconProxy is Proxy, Initializable {
    /**
     * @dev Initializes the proxy with `beacon`.
     *
     * If `data` is nonempty, it's used as data in a delegate call to the implementation returned by the beacon. This
     * will typically be an encoded function call, and allows initializing the storage of the proxy like a Solidity
     * constructor.
     *
     * Requirements:
     *
     * - `beacon` must be a contract with the interface {IBeacon}.
     * - If `data` is empty, `msg.value` must be zero.
     */
    function initialize(
        address beacon,
        bytes memory data
    ) external initializer {
        ERC1967Utils.upgradeBeaconToAndCall(beacon, data);
    }
}
```
The Initializable contract will set the INITIALIZABLE_STORAGE slot to 1 when the initializer modifier is triggered in the initialize function. Because of the lack of cleaning upper bits, it is theoretically possible to pass the INITIALIZABLE_STORAGE slot to the removeOwner function as the owner to be removed. Because the data stored in INITIALIZABLE_STORAGE has a value of 1, the iszero(eq(sload(_owner), 1)) would pass, and the initializable value would be effectively set to zero.
```solidity
// TelcoinWallet.sol
function removeOwner() {
    let _owner := calldataload(0x4)
    // Check if the provided address is equal to 0xaa
    if eq(_owner, 0xaa) {
        revert(0, 0)
    }
    // Invalid if:
    //
    caller() != address() || state[_owner] != 1
    if or(
        // Checks whether the currently executing code was called by the
        // contract itself, and reverts if that's not the case.
        iszero(eq(caller(), address())),
        // _owner must currently be an owner.
        //
        // guaranteed to be >3.
        iszero(eq(sload(_owner), 1))
    ) {
        revert(0, 0)
    }
    sstore(_owner, 0) // Delete the mapping.
    stop()
}
```
This would make the ClonableBeaconProxy’s function callable again, allowing a malicious actor to change the beacon address and make the wallet be unaccessible forever (although due to considering gatekeepers and owners as TRUSTED roles, actually requires maliciously crafted calldata). Medium. language that indicates the codebase's restrictions and/or expected functionality. Issues that break these statements, irrespective of whether the impact is low/unknown, will be assigned Medium severity. High severity will be applied only if the issue falls into the High severity category in the judging guidelines.” Considering the following excerpt from the contest’s README: “Data that is not properly signed by an authorized gatekeeper or wallet owner should be rejected by the wallet” As described in the README, data submitted to the wallet with dirty upper bits (which falls in the category of NOT properly signed data, even if it is submitted by a gatekeeper/owner) should be rejected. However, the wallet doesn’t actually reject this data and will instead accept it, effectively breaking the expected functionality of the wallet of rejecting data that is not properly signed. Because of this, this bug is of medium impact. Not performing a crucial step when dealing with low-level code will lead to unexpected outcomes, with different impacts ranging from the wallet remaining locked forever to transactions failing.

## Recommendation
Clean the upper bits of all the code variables that store data smaller than 32 bytes, especially the addresses in addOwner, removeOwner, replaceGatekeeper and the v value in __ecrecover.
