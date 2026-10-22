# [M] Hyperlane fee is always under-

## Summary
Severity: Medium
Contest weight: 0.4474
Dataset id: 1827
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hyperlane fee that is quoted and extracted from the sender while calling RootMessageBridge.sendMessage(...) doesn't take into account the additional gasLimit specified in the RootHLMessageModule contract. This results in the permanent DoS of the functionality as it's not possible to pay for the required fee.  
RootMessageBridge.sendMessage(...) function determines the Hyperlane fee without considering the enforced gasLimit specified in the RootHLMessageModule for each action. As a result fee passed and extracted from the sender will always correspond to the message delivery with the default gasLimit(50k) while the actual message fee should be paid for much higher gas limits.  
See the following PoC:  
```solidity
function testQuoteDispatch() public {
    IMailbox mailbox = IMailbox(0xd4C1905BB1D26BC93DAC913e13CaCC278CdCC80D);
    vm.createSelectFork("https://mainnet.optimism.io", 126570298);
    uint256 fee = mailbox.quoteDispatch(43114,
        TypeCasts.addressToBytes32(address(this)), "");
    console.log("fee: ", fee);
    bytes memory _metadata =
        StandardHookMetadata.formatMetadata({
            _msgValue: 0,
            _gasLimit: 2_000_000,
            _refundAddress: address(mailbox),
            _customMetadata: ""
        });
    fee = mailbox.quoteDispatch(43114,
        TypeCasts.addressToBytes32(address(this)), "", _metadata);
    console.log("fee: ", fee);
}
```
Mailbox.dispatch(...) function call with additional gasLimit specified in the defaultHookMetadata will always require a higher fee.  
As the fee is not enough to cover the cost for Mailbox.dispatch(...) this will result in the permanent DoS of RootMessageBridge.sendMessage(...) function.

## Recommendation
Fee extracted should always be quoted with the same parameters that are passed to the actual dispatch function call. Mailbox.quoteDispatch() function that allows passing defaultHookMetadata should be used for quoting.
