# [H] Underlying liquidity position is not transferred when fully unwrapping through the partial unwrap overload

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23484
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: While the ERC721WrapperBase partial unwrap overload is intended for use following partial liqui-
dations, it is possible for the sole holder of an ERC-6909 token to use this function to perform a full unwrap by
specifying the the total supply of the corresponding tokenId:
```solidity
function unwrap(address from, uint256 tokenId, address to, uint256 amount, bytes calldata extraData)
    external
    callThroughEVC
{
    _unwrap(to, tokenId, amount, extraData);
    _burnFrom(from, tokenId, amount);
}
```
The proportional share calculations implemented in the virtual `_unwrap()` will be executed to transfer the underlying
principal balance plus LP fees to the sole holder, before burning the the entire ERC-6909 token supply and leaving
the empty liquidity position NFT in the wrapper contract.  
Given that the total supply of ERC-6909 tokens is now reduced to zero following such a call, the position can still
be retrieved by performing a full unwrap of said empty position:
```solidity
function unwrap(address from, uint256 tokenId, address to) external callThroughEVC {
    _burnFrom(from, tokenId, totalSupply(tokenId));
    underlying.transferFrom(address(this), to, tokenId);
}
```
The caveat is that this can be performed by anyone, since `_burnFrom()` invoked with a zero amount will succeed
for any sender without reverting:
// ERC721WrapperBase
```solidity
function _burnFrom(address from, uint256 tokenId, uint256 amount) internal {
    address sender = _msgSender();
    if (from != sender && !isOperator(from, sender)) {
        _spendAllowance(from, sender, tokenId, amount);
    }
    _burn(from, tokenId, amount);
}
```
ERC6909
```solidity
function _burn(address from, uint256 id, uint256 amount) internal {
    if (from == address(0)) {
        revert ERC6909InvalidSender(address(0));
    }
    _update(from, address(0), id, amount);
}
```
ERC721WrapperBase
```solidity
function _update(address from, address to, uint256 id, uint256 amount) internal virtual override {
    super._update(from, to, id, amount);
    if (from != address(0)) evc.requireAccountStatusCheck(from);
}
```
ERC6909
```solidity
function _update(address from, address to, uint256 id, uint256 amount) internal virtual {
    address caller = _msgSender();
    if (from != address(0)) {
        uint256 fromBalance = _balances[from][id];
        if (fromBalance < amount) {
            revert ERC6909InsufficientBalance(from, fromBalance, amount, id);
        }
        unchecked {
            // Overflow not possible: amount <= fromBalance.
            _balances[from][id] = fromBalance - amount;
        }
    }
    if (to != address(0)) {
        _balances[to][id] += amount;
    }
    emit Transfer(caller, from, to, id, amount);
}
```
This may not be desirable as a user who unwraps their position in this way may have their NFT retrieved or even
burnt by a different account, and it will not be possible for them to mint the same tokenId once again.  
Impact: An empty Uniswap V4 position remaining in the wrapper contract following full unwrap via the partial
unwrap overload can be recovered and re‑used by any sender by subsequently invoking the full unwrap and re‑wrapping.

## Proof of Concept
```solidity
function test_unwrapPoC() public {
    LiquidityParams memory params = LiquidityParams({
        tickLower: TickMath.MIN_TICK + 1,
        tickUpper: TickMath.MAX_TICK - 1,
        liquidityDelta: -19999
    });
    (uint256 tokenId1,,) = boundLiquidityParamsAndMint(params);
    startHoax(borrower);
    // 1. borrower wraps tokenId1
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.wrap(tokenId1, borrower);
    // 2. borrower fully unwraps via partial unwrap
    wrapper.unwrap(
        borrower,
        tokenId1,
        borrower,
        wrapper.FULL_AMOUNT(),
        bytes("")
    );
    // 3. borrower retrieves the empty position via full unwrap
    wrapper.unwrap(
        borrower,
        tokenId1,
        borrower
    );
    // 4. borrower re-wraps the position
    wrapper.underlying().approve(address(wrapper), tokenId1);
    wrapper.wrap(tokenId1, borrower);
}
```

## Recommendation
Recommended Mitigation: If the total supply of a given ERC-6909 token is reduced to zero following a partial
unwrap, consider also transferring the underlying NFT to the recipient.
