# [M] Gas parameters for Stargate swap are hard-

## Summary
Severity: Medium
Contest weight: 0.6044
Dataset id: 22544
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The dstGasForCall for transferring erc20s through Stargate is hardcoded to 0 in the Balancer contract leading to sgReceive not being called during Stargate swap. As a consequence, the sgReceive has to be manually called to clear the cachedSwapLookup mapping, but this can be DoSed due to the fact that the mTOFT::sgReceive doesn't validate any of its parameters. This can be exploited to perform a long-term DoS attack. Gas parameters for Stargate Swap allows the caller to specify the:
• dstGasForCall which is the gas amount forwarded while calling the sgReceive on the destination contract.
• dstNativeAmount and dstNativeAddr which is the amount and address where the native token is sent to.
Inside the Balancer.sol contract, the dstGasForCall is hardcoded to 0. The dstGasForCall gets forwarded from Stargate Router into the Stargate Bridge contract.
```solidity
function swap(
    uint16 _chainId,
    uint256 _srcPoolId,
    uint256 _dstPoolId,
    address payable _refundAddress,
    Pool.CreditObj memory _c,
    Pool.SwapObj memory _s,
    IStargateRouter.lzTxObj memory _lzTxParams,
    bytes calldata _to,
    bytes calldata _payload
) external payable onlyRouter {
    bytes memory payload = abi.encode(TYPE_SWAP_REMOTE, _srcPoolId, _dstPoolId, _lzTxParams.dstGasForCall, _c, _s, _to, _payload);
    _call(_chainId, TYPE_SWAP_REMOTE, _refundAddress, _lzTxParams, payload);
}

function _call(
    uint16 _chainId,
    uint8 _type,
    address payable _refundAddress,
    IStargateRouter.lzTxObj memory _lzTxParams,
    bytes memory _payload
) internal {
    bytes memory lzTxParamBuilt = _txParamBuilder(_chainId, _type, _lzTxParams);
    uint64 nextNonce = layerZeroEndpoint.getOutboundNonce(_chainId, address(this)) + 1;
    layerZeroEndpoint.send{value: msg.value}(_chainId, bridgeLookup[_chainId], _payload, _refundAddress, address(this), lzTxParamBuilt);
    emit SendMsg(_type, nextNonce);
}
```
It gets encoded inside the payload that is sent through the LayerZero message. The payload gets decoded inside the Bridge::lzReceive on destination chain. And dstGasForCall is forwarded to the sgReceive function:

## Recommendation
The dstGasForCall shouldn't be hardcoded to 0. It should be a configurable value that is set by the admin of the Balancer contract. Take into account that this value will be different for different chains. For instance, Arbitrum has a different gas model than Ethereum due to its specific precompiles: https://docs.arbitrum.io/arbos/gas. The recommended solution is:
```solidity
contract Balancer is Ownable {
    using SafeERC20 for IERC20;

    mapping(uint16 => uint256) internal sgReceiveGas;

    function setSgReceiveGas(uint16 eid, uint256 gas) external onlyOwner {
        sgReceiveGas[eid] = gas;
    }

    function getSgReceiveGas(uint16 eid) internal view returns (uint256) {
        uint256 gas = sgReceiveGas[eid];
        if (gas == 0) revert();
        return gas;
    }

    IStargateRouterBase.lzTxObj({dstGasForCall: getSgReceiveGas(_dstChainId), dstNativeAmount: 0, dstNativeAddr: "0x0"}),
```
