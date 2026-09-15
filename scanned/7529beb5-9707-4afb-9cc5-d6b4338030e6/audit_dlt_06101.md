# [M] Curve Reentrancy Guard will not work if the pool implements a fallback

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-30
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/52
Type: hats-finding

## Details
**Github username:** @GalloDaSballo
**Submission hash (on-chain):** 0x452fbd793a0e0e2cc2cfc7197efd6862bac5723a1e389d5fe49c2446782082c3
**Severity:** medium severity

**Description:**
**Description**\
The Reentrancy Guard for Curve is based on the idea that one of the functions called should pass, and passing is a guarantee that the guard was engaged.

That is not the case for Vyper Contract that implement a fallback via `__default__`

The most notable example being Tricrypto on Mainnet: 0xD51a44d3FaE010294C616388b506AcdA1bfAAE46

**Attack Scenario**\
Such a pool is added, reentrancy guard becomes ineffective

**Attachments / POC**

The following POC is written in brownie, just add the contracts and interfaces, then follow the instructions

The goal of the POC is to demonstrate:
1) Tricrypto will not revert if you transfer with some data
2) Fake Curve Pool just implements the fallback
3) If we call a pool with just a fallback, the first try catch in which a function expects no return value will pass, marking the pool as reentrancy safe

## Open Up the Console via
brownie console --network mainnet-fork



## Setup: paste in the console
```python
## Proof fallback is implemented in tricrypto
a[0].transfer("0xD51a44d3FaE010294C616388b506AcdA1bfAAE46", 0, data="0x123")


## Deploy fake pool
fake = FakeCurvePool.deploy({"from": a[0]})
## Proof fallback is working
a[0].transfer(fake, 1, data="0x123")

lib = CurveLibrary.deploy({"from": a[0]})
```

## POC

Calling it will result in:

```python
>>> history[-1].events
{'Debug': [OrderedDict([('name', 'Call 1')]), OrderedDict([('name', 'try_remove_liquidity_one_coin b4 try')]), OrderedDict([('name', 'Success One Coin')])]}
>>> lib.check_reentrancy(fake, 3, {"from": a[0]})
Transaction sent: 0x2cb6d71b33404985be67febb5e52b8ea0a35cb8c4566d9e52a3250ce32aaf9c1
  Gas price: 0.0 gwei   Gas limit: 12000000   Nonce: 15
  CurveLibrary.check_reentrancy confirmed   Block: 17591157   Gas used: 28765 (0.24%)

<Transaction '0x2cb6d71b33404985be67febb5e52b8ea0a35cb8c4566d9e52a3250ce32aaf9c1'>
>>> history[-1].events
{'Debug': [OrderedDict([('name', 'Call 1')]), OrderedDict([('name', 'try_remove_liquidity_one_coin b4 try')]), OrderedDict([('name', 'Success One Coin')])]}
```


## Code

Fake Curve Pool simply has a receive (in line with TriCrypto on Mainnet)
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

// Fake pool that has a fallback
contract FakeCurvePool {
  fallback() payable external{

  }
}
```

Extracted from your CurveOracle

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "../interfaces/ICurvePool.sol";

contract CurveLibrary {
	event Debug(string name);

function try_remove_liquidity_3(address curve_pool) internal returns(bool){
    	uint[3] memory amounts = [uint(0), uint(0), uint(0)];
			emit Debug("try_remove_liquidity_3 b4 try");
		try ICurvePool(curve_pool).remove_liquidity(0, amounts) returns(uint256[3] memory) {
			return true;
		} catch {
			emit Debug("try_remove_liquidity_3 catch 1");
			try ICurvePool2(curve_pool).remove_liquidity(0, amounts) {
				return true;
			} catch {
				emit Debug("try_remove_liquidity_3 catch 2");
				return false;
			}
		}
	}
	function try_remove_liquidity_2(address curve_pool) internal returns(bool){
    	uint[2] memory amounts = [uint(0), uint(0)];

			emit Debug("try_remove_liquidity_2 b4 try");
		try ICurvePool(curve_pool).remove_liquidity(0, amounts) returns(uint256[2] memory) {
			return true;
		} catch {
			emit Debug("try_remove_liquidity_2 catch 1");
			try ICurvePool2(curve_pool).remove_liquidity(0, amounts) {
				return true;
			} catch {
				emit Debug("try_remove_liquidity_2 catch 2");
				return false;
			}
		}
	}

	function try_remove_liquidity_one_coin(address curve_pool) internal returns(bool){
		emit Debug("try_remove_liquidity_one_coin b4 try");
		try ICurvePool(curve_pool).remove_liquidity_one_coin(0,1,0) { // Seems like this breaks if you don't have 1 wei
			return true;
		} catch {
			emit Debug("try_remove_liquidity_one_coin catch 1");
			try ICurvePool2(curve_pool).remove_liquidity_one_coin(0,1,0) returns(uint256){
				return true;
			} catch {
				emit Debug("try_remove_liquidity_one_coin catch 2");
				return false;
			}
		}
	}

	

	/**
     * @dev Helper to prevent read-only re-entrancy attacks with virtual price. Only needed if the underlying has ETH.
     * @param curve_pool The curve pool address (not the token address!)
     **/
	function check_reentrancy(address curve_pool, uint256 num_tokens) external {
		emit Debug("Call 1");
		if(try_remove_liquidity_one_coin(curve_pool)){
			emit Debug("Success One Coin");
			return;
		}
		emit Debug("Call 2");
		if(num_tokens==2 && try_remove_liquidity_2(curve_pool)){
			emit Debug("Success Two Coins");
			return;
		}
		emit Debug("Call 3");
		if(num_tokens==3 && try_remove_liquidity_3(curve_pool)){
			emit Debug("Success Three Coin");
			return;
		}
		emit Debug("Call 4");
		uint[3] memory amounts = [uint(0), uint(0), uint(0)];
		ICurvePool2(curve_pool).remove_liquidity(0, amounts); //
		emit Debug("Will Revert no matter what");
		revert("End of the line");
	}

	receive() external payable {
	}
}

```
