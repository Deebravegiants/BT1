# [H] OneInchV6Guard insufficient checks allow man-

## Summary
Severity: High
Contest weight: 0.7878
Dataset id: 22935
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
OneInchV6Guard insufficient checks allow manager to steal tokens via unoswap swaps. Managers and traders can execute transactions on the funds in the pool via the execTransaction function. The transactions are first checked by the contract guards of the destination. One such destination is the OneInch contract. Managers and traders are not trusted members. They are not expected to be able to draw out funds from the pool. The OneInchV6Guard.sol contract makes sure that the managers and traders cannot take out too much value from the pool. This is done via the slippage accumulator.
The _verifySwap function checks the swap parameters, and especially the swap input and output assets+amounts. The slippage accumulator checks the total value in and the total value out, and makes sure that the loss is within limits specified by the protocol owners.
Thus swapData.srcAmount and swapData.dstAmount are crucial numbers. The issue is that in the unoswap modules of oneinch, the swapData.dstAmount can be faked. The manager passes in the pool address and the dstAmount, which can be bad values and bad contracts.
```solidity
(uint256 srcToken, uint256 srcAmount, uint256 dstAmount, uint256 pool) = abi.decode(
    params,
    (uint256, uint256, uint256, uint256)
);
```
A check is done on the pool address, with _checkProtocolsSupported(pools), but if the pool is malicious, it can easily pass this check since the calls are done on the pool itself.
```solidity
ProtocolLib.Protocol protocol = _pools[i].protocol();
require(
    protocol == ProtocolLib.Protocol.UniswapV2 || protocol == ProtocolLib.Protocol.UniswapV3,
    "exchange pool not supported"
);
require(!_pools[i].shouldUnwrapWeth(), "WETH unwrap not supported");
```
As seen above, the pool has to implement a protocol() function which returns UniswapV2 or UniswapV3. This is easily faked. So now the last hope is that the Oneinch router itself ensures that at least destAmount amount of tokens are paid out, or that pool address is checked. To verify this, we check the router contract at 0x111111125421cA6dc452d289314280a0f8842A65 on the mainnet. In the router, the _unoswapTo function is called, which calls the _unoswap function.
```solidity
function _unoswap(
    address spender,
    address recipient,
    Address token,
    uint256 amount,
    uint256 minReturn,
    Address dex
) private returns(uint256 returnAmount) {
    ProtocolLib.Protocol protocol = dex.protocol();
    if (protocol == ProtocolLib.Protocol.UniswapV3) {
        returnAmount = _unoswapV3(spender, recipient, amount, minReturn, dex);
    } else if (protocol == ProtocolLib.Protocol.UniswapV2) {
        if (spender == address(this)) {
            IERC20(token.get()).safeTransfer(dex.get(), amount);
        } else if (spender == msg.sender) {
            IERC20(token.get()).safeTransferFromUniversal(msg.sender, dex.get(), amount, dex.usePermit2());
        }
        returnAmount = _unoswapV2(recipient, amount, minReturn, dex);
    } else if (protocol == ProtocolLib.Protocol.Curve) {
        if (spender == msg.sender && msg.value == 0) {
            IERC20(token.get()).safeTransferFromUniversal(msg.sender, address(this), amount, dex.usePermit2());
        }
        returnAmount = _curfe(recipient, amount, minReturn, dex);
    }
}
```
As we can see above, pool is not verified. Only a view function is called in the pool which can be faked. So pool (here dex) can be a malicious contract which returns bad values. In both the _unoswapV3 and _unoswapV2 functions, the swap() function is called on uni V2 or V3 pools, and the return value is checked against minReturn. If the pool is malicious, it can take all the input tokens, pay out 0 output tokens, and still return a returnAmount which is higher than the minReturn. So we have established that the pool address is not sufficiently checked by either the OneInchV6Guard or the OneInch router so it can be malicious. The actual token transfer amounts are not checked, and only the returns value is checked, which can be fake. So if the manager decides to steal everything from the pool, they can deploy a pool contract which takes out tokens from the router, and returns an appropriate returnAmount and has the necessary view only functions. They can then call the execTransaction function with the pool address, and drain the pool of all funds. The slippage accumulator will not be triggered, since it works off of the return value from the pool. Draining of the pool by the manager/trader is explicitly forbidden by the protocol. Thus this is a high severity issue. Entire pool can be drained by the manager or trader.

## Recommendation
Check if pool is a legit pool by calling and checking with the uni V2 or V3 or the curve factory contract and verifying it. The factory contracts generally have a way to check if an address is a pool deployed by them or not.
