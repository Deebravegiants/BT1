# [M] Token bridges process messages

## Summary
Severity: Medium
Contest weight: 0.5775
Dataset id: 1821
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Messages sent from unsupported chains will be processed by the Token Bridge, which might lead to unauthorized minting of XVELO if they are malicious.  
The Token Bridge was found not to restrict messages from only supported chains. As a result, it might lead to the following issues:  
• When the admin removes a supported chain from the protocol via the deregisterChain function, the Token Bridge will still continue to process messages sent from the unsupported chains.  
• Although it is unlikely that the attacker will be able to deploy a TokenBridge with the same address on another chain because they do not have Velodrome's deployer's private key, however, since Hyperlane supports 60+ chains, there might be a possibility that one of them has some bugs that attackers can exploit to obtain the same address and perform authorized minting of XVELO. Thus, the Token Bridge should only process messages from chains that are approved by the admin.  
```solidity
/// @inheritdoc IHLHandler
function handle(uint32 _origin, bytes32 _sender, bytes calldata _message)
    external payable {
    if (msg.sender != mailbox) revert NotMailbox();
    if (_sender != TypeCasts.addressToBytes32(address(this))) revert NotBridge();

    (address recipient, uint256 amount) = _message.recipientAndAmount();

    IXERC20(xerc20).mint({_user: recipient, _amount: amount});
}
```

## Recommendation
Consider only processing messages from supported chains.  
```solidity
function handle(uint32 _origin, bytes32 _sender, bytes calldata _message) external payable {
    if (msg.sender != mailbox) revert NotMailbox();
    if (_sender != TypeCasts.addressToBytes32(address(this))) revert NotBridge();
    if (!_chainids.contains({value: _origin})) revert UnsupportedChain();
    (address recipient, uint256 amount) = _message.recipientAndAmount();
    IXERC20(xerc20).mint({_user: recipient, _amount: amount});
}
```
