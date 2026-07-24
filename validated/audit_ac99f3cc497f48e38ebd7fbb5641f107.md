### Title
Fee-on-Transfer Token Inflates Cross-Chain Credit, Breaking Backing Guarantee — (`evm/src/omni-bridge/contracts/OmniBridge.sol`)

### Summary
`initTransfer` in `OmniBridge.sol` records and broadcasts the caller-supplied `amount` rather than the actual tokens received by the contract. For any ERC20 token that deducts a transfer fee, the bridge locks fewer tokens than it credits on the destination chain, creating unbacked wrapped supply that cannot be fully redeemed.

### Finding Description
In `initTransfer`, when the token is neither a bridge-deployed token nor a custom-minter token, the contract executes a plain `safeTransferFrom`: [1](#0-0) 

The contract then immediately passes the original caller-supplied `amount` — not the actual balance delta — to `initTransferExtension` and to the `InitTransfer` event: [2](#0-1) 

`OmniBridgeWormhole.initTransferExtension` encodes this same `amount` verbatim into the Wormhole VAA that is relayed to NEAR: [3](#0-2) 

For a fee-on-transfer token (e.g., USDT with fee enabled, PAXG, or any rebasing/deflationary ERC20), the bridge receives `amount - fee` tokens but the VAA tells NEAR to credit the user with `amount`. Every such deposit inflates the cross-chain supply by exactly the fee amount.

### Impact Explanation
This is a **backing guarantee break** (High/Critical). The EVM bridge vault becomes progressively undercollateralized: each fee-on-transfer deposit creates `fee` units of unbacked wrapped tokens on NEAR. When users bridge back, the last redeemers will find the bridge contract holds insufficient tokens, causing irreversible fund lock for those users. The discrepancy compounds with every deposit.

### Likelihood Explanation
The bridge explicitly supports arbitrary native ERC20 tokens (the `else` branch at line 406 is the general-purpose lock path). USDT on Ethereum already has the fee-charging code deployed (currently set to 0 but switchable by Tether). Any future token added to the bridge that charges transfer fees immediately triggers this path. No privileged access is required — any user calling `initTransfer` with a fee-on-transfer token triggers the accounting divergence.

### Recommendation
Use the balance-check pattern around the `safeTransferFrom` call to compute the actual received amount, and use that value for all downstream accounting, event emission, and cross-chain messaging:

```solidity
uint256 balanceBefore = IERC20(tokenAddress).balanceOf(address(this));
IERC20(tokenAddress).safeTransferFrom(msg.sender, address(this), amount);
uint256 actualReceived = IERC20(tokenAddress).balanceOf(address(this)) - balanceBefore;
// use actualReceived instead of amount going forward
``` [4](#0-3) 

### Proof of Concept
1. Assume token `T` charges a 1% fee on every `transferFrom`.
2. Attacker (or any user) calls `initTransfer(T, 1000e18, 0, 0, "alice.near", "")`.
3. `safeTransferFrom` moves 1000e18 from the caller but the bridge receives only 990e18 (1% fee taken).
4. `initTransferExtension` encodes `amount = 1000e18` into the Wormhole VAA.
5. NEAR processes the VAA and mints 1000e18 wrapped-T to `alice.near`.
6. The bridge holds only 990e18 T as backing for 1000e18 wrapped-T — 10e18 is unbacked.
7. Repeating this 100 times leaves the bridge holding 99,000e18 T but 100,000e18 wrapped-T in circulation; the last ~1% of redeemers cannot withdraw, permanently locking their funds.

### Citations

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L406-412)
```text
            } else {
                IERC20(tokenAddress).safeTransferFrom(
                    msg.sender,
                    address(this),
                    amount
                );
            }
```

**File:** evm/src/omni-bridge/contracts/OmniBridge.sol (L415-436)
```text
        initTransferExtension(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message,
            extensionValue
        );

        emit BridgeTypes.InitTransfer(
            msg.sender,
            tokenAddress,
            currentOriginNonce,
            amount,
            fee,
            nativeFee,
            recipient,
            message
        );
```

**File:** evm/src/omni-bridge/contracts/OmniBridgeWormhole.sol (L129-141)
```text
        bytes memory payload = bytes.concat(
            bytes1(uint8(MessageType.InitTransfer)),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(sender),
            bytes1(omniBridgeChainId),
            Borsh.encodeAddress(tokenAddress),
            Borsh.encodeUint64(originNonce),
            Borsh.encodeUint128(amount),
            Borsh.encodeUint128(fee),
            Borsh.encodeUint128(nativeFee),
            Borsh.encodeString(recipient),
            Borsh.encodeString(message)
        );
```
