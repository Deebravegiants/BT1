# [H] ERC20 Transfer/approve errors may go unnoticed

## Summary
Severity: High
Reporter: eierina
Source: https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol
Type: audit-issue

## Details
# ERC20 Transfer/approve errors may go unnoticed

## Summary

Telcoin contest supports a range of ERC20 tokens (that can also expand in future?), therefore it should take into account all the different ways of signalling success and failure.  This is not the case, as many ERC20's transfer(), transferFrom(), and approve() functions are either not verified at all or verified for returning true. As a result, depending on the ERC20 token, some transfer errors may result in passing unnoticed, and/or some successfull transfer may be treated as failed.

Currently the only supported ERC20 tokens are the ones that fulfill both the following requirements:
- always revert on failure;
- always returns boolean true on success.

An example of a very well known token that is not supported is Tether USD (USDT).

## Vulnerability Detail

Tokens have different ways of signalling success and failure, and this affect mostly transfer(), transferFrom() and approve() in ERC20 tokens. While some tokens revert upon failure, others consistently return boolean flags to indicate success or failure, and many others have mixed behaviours.

See below a snippet of the [USDT Token contract](https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7#code#L1) compared to the 0x's [ZRX Token contract](https://etherscan.io/token/0xe41d2489571d322189246dafa5ebde1f4699f498#code#L1) where the USDT Token transfer function does not even return a boolean value, while the ZRX token consistently returns boolean value hence returning false on failure instead of reverting.

***USDT Token snippet (no return value) from Etherscan***
```solidity
function transferFrom(address _from, address _to, uint _value) public onlyPayloadSize(3 * 32) {
	var _allowance = allowed[_from][msg.sender];

	// Check is not needed because sub(_allowance, _value) will already throw if this condition is not met
	// if (_value > _allowance) throw;

	uint fee = (_value.mul(basisPointsRate)).div(10000);
	if (fee > maximumFee) {
		fee = maximumFee;
	}
	if (_allowance < MAX_UINT) {
		allowed[_from][msg.sender] = _allowance.sub(_value);
	}
	uint sendAmount = _value.sub(fee);
	balances[_from] = balances[_from].sub(_value);
	balances[_to] = balances[_to].add(sendAmount);
	if (fee > 0) {
		balances[owner] = balances[owner].add(fee);
		Transfer(_from, owner, fee);
	}
	Transfer(_from, _to, sendAmount);
}
```

***ZRX Token snippet (consistently true or false boolean result) from Etherscan***
```solidity
function transferFrom(address _from, address _to, uint _value) returns (bool) {
	if (balances[_from] >= _value && allowed[_from][msg.sender] >= _value && balances[_to] + _value >= balances[_to]) {
		balances[_to] += _value;
		balances[_from] -= _value;
		allowed[_from][msg.sender] -= _value;
		Transfer(_from, _to, _value);
		return true;
	} else { return false; }
}
```

## Impact

Given the different of token transfers in [FeeBuyBack.sol](https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol), if the ERC20 token being transferred is one that consistently returns a boolean result in the case of success and failure like for example [0x](https://www.0x.org/)'s [ZRX Token contract](https://etherscan.io/token/0xe41d2489571d322189246dafa5ebde1f4699f498#code#L1), where the return value is currently not verified to be true, the transfer may fail (e.g.: no tokens transferred due to insufficient balance) but the error would not be detected by the project contracts.

Same is true for appove calls.

## Code Snippet

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L62-L63

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L71-L72

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L79

https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/fee-buyback/FeeBuyback.sol#L95

Some similare usages in InsecureWallet.sol and YieldSource.sol but they seems not to be in scope for this contest.

## Tool used

Manual Review

## Recommendation
To handle most of these inconsistent behaviors across multiple tokens, either use OpenZeppelin's [SafeERC20 library](https://docs.openzeppelin.com/contracts/4.x/api/token/erc20#SafeERC20), or use a more reusable implementation (i.e. library) of the following intentionally explicit, descriptive example code for an ERC20 transferFrom() call that takes into account all the different ways of signalling success and failure, and apply to all ERC20 transfer(), transferFrom(), approve() calls in the project contracts.

```solidity
IERC20 token = whatever_token;

(bool success, bytes memory returndata) = address(token).call(abi.encodeWithSelector(IERC20.transferFrom.selector, sender, recipient, amount));

// if success == false, without any doubts there was an error and callee reverted
require(success, "Transfer failed!");

// if success == true, we need to check whether we got a return value or not (like in the case of USDT)
if (returndata.length > 0) {
	// we got a return value, it must be a boolean and it should be true
	require(abi.decode(returndata, (bool)), "Transfer failed!");
} else {
	// since we got no return value it can be one of two cases:
	// 1. the transferFrom does not return a boolean and it did succeed
	// 2. the token address is not a contract address therefore call() always return success = true as per EVM design
	// To discriminate between 1 and 2, we need to check if the address actually points to a contract
	require(address(token).code.length > 0, "Not a token address!");
}
```
