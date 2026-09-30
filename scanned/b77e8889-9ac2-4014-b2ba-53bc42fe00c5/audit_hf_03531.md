# [H] if the Virtual Account’s owner is a Contract Account

## Summary
Severity: High
Contest weight: 0.8359
Dataset id: 19303
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the way the RootBridgeAgent contract resolves a user’s Virtual Account when processing cross‑chain messages. The fetchVirtualAccount function in the RootPort contract receives only a plain Ethereum address that originated from the BranchBridgeAgent payload and uses this address to look up or create a Virtual Account, without taking the originating branch (source chain) into account. Consequently, if the caller on the source chain is a contract account – for example a Gnosis Safe or any multisig wallet – an attacker who can obtain control of a contract with the same address on a different branch can impersonate the original depositor. By sending a signed cross‑chain message from the compromised branch, the attacker triggers RootBridgeAgent to fetch the Virtual Account associated with that address, which the system mistakenly assumes belongs to the original user. The attacker can then invoke the withdrawal logic, causing the Root environment to transfer all assets held in the Virtual Account to the attacker’s address on the target branch. This flaw is a classic cross‑chain identity‑confusion bug where ownership is bound only to an address, not to the (address, chain) pair, and where contract accounts are treated the same as externally owned accounts (EOAs). Exploitation requires the attacker to control a contract at the same address on another chain – a scenario that is feasible with deterministic deployment techniques such as CREATE2 or by compromising a Gnosis Safe deployment on that chain. When the attack succeeds, the victim sees their balance in the Root environment drop to zero, receives no refund or withdrawal confirmation, and may observe that a transaction they did not initiate has been processed. The issue is difficult to notice because the address used in the payload matches the user’s wallet address, the UI shows a normal transaction hash, and there is no explicit indication that the call originated from a different branch. The bug was discovered during a manual audit that examined the cross‑chain message handling logic and identified that the source‑chain identifier was never validated when fetching the Virtual Account. To remediate, the protocol should bind each Virtual Account to both the owner address and the source chain identifier, and it should include a flag in the cross‑chain payload indicating whether the caller is a contract or an EOA. The RootBridgeAgent must verify that the caller’s address is authorized on the originating branch before granting access to the Virtual Account, and it should reject or re‑assign ownership if the caller originates from a different branch. In short, the fix consists of adding explicit source‑chain validation and contract‑account checks so that only the original branch that created the Virtual Account can later manipulate it, thereby preventing unauthorized withdrawals and protecting user funds.

## Proof of Concept
* When sending signed messages from a Branch to Root, the RootBridgeAgent contract calls the [`RootPort::fetchVirtualAccount()`](https://github.com/code-423n4/2023-09-maia/blob/main/src/RootPort.sol#L350-L353) to get the Virtual Account that is assigned in the Root environment to the address who initiated the call in the SrcBranch; if that address doesn’t have an assigned Virtual Account yet, it proceeds to create one and assign it.
  * The problem is that the `fetchVirtualAccount()` function solely relies on the address of the caller in the SrcBranch; however, it doesn’t take into account from _which_ Branch the call comes.

**BranchBridgeAgent.sol:**
```solidity
function callOutSignedAndBridge(
    ...
) external payable override lock {
  ...
  //Encode Data for cross-chain call.
  bytes memory payload = abi.encodePacked(
      _hasFallbackToggled ? bytes1(0x85) : bytes1(0x05),
      //@audit-info => Encodes the address of the caller in the Branch and sends it to the RootBridgeAgent
      //@audit-info => This address will be used to fetch the VirtualAccount assigned to it!
      msg.sender,
      _depositNonce,
      _dParams.hToken,
      _dParams.token,
      _dParams.amount,
      _dParams.deposit,
      _params
  );
}
```

**RootBridgeAgent.sol:**
```solidity
function lzReceiveNonBlocking(
  ...
) public override requiresEndpoint(_endpoint, _srcChainId, _srcAddress) {
  ...
  ...
  ...
  else if (_payload[0] == 0x04) {
      // Parse deposit nonce
      nonce = uint32(bytes4(_payload[PARAMS_START_SIGNED:PARAMS_TKN_START_SIGNED]));

      //Check if tx has already been executed
      if (executionState[_srcChainId][nonce] != STATUS_READY) {
          revert AlreadyExecutedTransaction();
      }

      //@audit-info => Reads the address of the msg.sender in the BranchBridgeAgent and forwards that address to the RootPort::fetchVirtualAccount()
      // Get User Virtual Account
      VirtualAccount userAccount = IPort(localPortAddress).fetchVirtualAccount(
          address(uint160(bytes20(_payload[PARAMS_START:PARAMS_START_SIGNED])))
      );

      // Toggle Router Virtual Account use for tx execution
      IPort(localPortAddress).toggleVirtualAccountApproved(userAccount, localRouterAddress);

    ...
    ...
  }
  ...
  ...
}
```

**RootPort.sol:**
```solidity
//@audit-info => Receives from the RootBridgeAgent contract the address of the caller in the BranchBridgeAgent contract
//@audit-info => Fetches the VirtualAccount assigned to the _user address regardless from what Branch the call came from
function fetchVirtualAccount(address _user) external override returns (VirtualAccount account) {
    account = getUserAccount[_user];
    if (address(account) == address(0)) account = addVirtualAccount(_user);
}
```
Like the example, let’s suppose that a user uses a MultiSigWallet contract to deposit tokens from Avax to Root, in the RootBridgeAgent contract. The address of the MultisigWallet will be used to create a Virtual Account, and all the `globalTokens` that were bridged will be deposited in this Virtual Account.

Now, the problem is that the address of the MultisigWallet, might not be controlled by the same user on a different chain. For example, in Polygon, an attacker could gain control of the address of the same address of the MultisigWallet that was used to deposit tokens from Avax in the Root environment. An attacker can send a signed message from Polygon, using the same address of the MultisigWallet that deposited tokens from Avax, to the Root environment, requesting to withdraw the assets that the Virtual Account is holding in the Root environment to the Polygon Branch.

When the message is processed by the Root environment, the address that will be used to obtain the Virtual Account will be the address that initiated the call in Polygon; which will be the same address of the user’s MultisigWallet contract who deposited the assets from Avax. However, the Root environment, when fetching the virtual account, makes no distinctions between the branches. Thus, it will give access to the Virtual Account of the attacker’s caller address and process the message in the Root environment.

As a result, an attacker can gain control of the Virtual Account of an account contract that was used to deposit assets from a chain into Root, by gaining control of the same address of the account contract that deposited the assets in a different chain.

As explained in detail on this [article written by Rekt](https://rekt.news/wintermute-rekt/), it is possible to gain control of the same address for contract accounts in a different chain; especially for those contract accounts that are deployed using the Gnosis Safe contracts:

![SafeWallet Rekt Article Write Up](https://user-images.githubusercontent.com/135237830/283603636-43f35ddc-3017-4055-8f17-bc833f6ccc1f.png)

## Recommendation
The recommendation is to add some logic that validates if the caller address in the BranchBridgeAgent is a contract account or an EOA. If it’s a contract account, send a special flag as part of the crosschain message, so that the RootBridgeAgent contract can know if the caller in the SrcBranch it’s a contract or an EOA.

  * If the caller is an EOA, the caller’s address can be assigned as the Virtual Account owner on all the chains, for EOAs there are no problems.
  * But, if the caller is a Contract Account, when fetching the virtual account forward to the SrcChain, and if a Virtual Account is created, authorize the caller address on the SrcBranch as the owner for that Virtual Account. This way, only the contract account in the SrcBranch can access the Virtual Account in the Root environment.

Make sure to use the `srcChainId` to validate if the caller is an owner of the Virtual Account.
