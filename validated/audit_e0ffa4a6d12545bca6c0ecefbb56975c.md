No vulnerability found for this question.

The ERC-6492 bug class requires a signature-checking library that decodes an attacker-supplied payload into a factory address + arbitrary calldata and executes that call as part of signature validation, with no separation between the untrusted call and the caller's own storage/funds. Alt.fun's only signature-consuming code path is `Zap._tryPermit`, which forwards a standard EIP-2612 `(v, r, s)` tuple directly to the token's own `IERC20Permit.permit` function [1](#0-0) . This is a plain ECDSA-recovery permit call (as implemented by OpenZeppelin's `ERC20Permit.permit`, which recovers the signer via `ECDSA.recover` and compares to `owner`) [2](#0-1)  — there is no factory address, no arbitrary calldata blob, and no `isValidSignature`/`isValidERC6492SignatureNow`-style dispatch anywhere in `packages/contracts/src` that would let a caller embed an arbitrary call target and payload inside a "signature" argument. `PermitData` in `Zap.sol` is a fixed `{value, deadline, v, r, s}` struct, not an opaque bytes blob that could smuggle a call target [3](#0-2) .

None of alt.fun's actual attack surfaces (bonding-curve math, LT rebasing reads, Zap's USDC→LT→token layering, dual graduation triggers, two-phase graduation, or HyperSwap V2 LP seeding) involve signature-driven arbitrary calls, so this report's bug class has no reachable analog in the in-scope contracts.

### Citations

**File:** packages/contracts/src/Zap.sol (L93-99)
```text
    struct PermitData {
        uint256 value;
        uint256 deadline;
        uint8 v;
        bytes32 r;
        bytes32 s;
    }
```

**File:** packages/contracts/src/Zap.sol (L491-503)
```text
    /// @dev Catch swallows reverts to defuse permit-front-run DoS: if an
    ///      attacker submits the same sig first the nonce is consumed but the
    ///      allowance is already set, so the follow-on `transferFrom`
    ///      succeeds. A genuinely bad permit is caught downstream by the
    ///      transfer reverting on insufficient allowance — frontends should
    ///      simulate to surface a permit-specific error pre-flight.
    function _tryPermit(
        address token,
        address owner_,
        PermitData calldata p
    ) internal {
        try IERC20Permit(token).permit(owner_, address(this), p.value, p.deadline, p.v, p.r, p.s) {} catch {}
    }
```

**File:** packages/contracts/lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Permit.sol (L42-60)
```text
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public virtual {
        if (block.timestamp > deadline) {
            revert ERC2612ExpiredSignature(deadline);
        }

        bytes32 structHash = keccak256(abi.encode(PERMIT_TYPEHASH, owner, spender, value, _useNonce(owner), deadline));

        bytes32 hash = _hashTypedDataV4(structHash);

        address signer = ECDSA.recover(hash, v, r, s);
        if (signer != owner) {
```
