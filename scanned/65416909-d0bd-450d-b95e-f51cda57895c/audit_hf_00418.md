# [M] Token bridging with Hyperlane

## Summary
Severity: Medium
Contest weight: 0.1854
Dataset id: 1826
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Token bridging through Hyperlane doesn't allow the user to specify the gas limit for message delivery on the destination chain leading to stuck messages, i.e. needing manual intervention to deliver the message.  
There is also no refund mechanism for sending msg.value that is higher than the Hyperlane fee as default hooks for Hyperlane don't refund.  
TokenBridge.sendToken(...) function calls Mailbox.dispatch(...) function with default parameters, i.e. doesn't allow specifying additional gas for message delivery. The default gasLimit is 50k and this might not be sufficient to execute the handle function on the destination chain and bridge the tokens. The only option the user has is paying for additional gas through InterchainGasPaymaster.payForGas(...) function call. This is not ideal as user needs to monitor the delivery of his message and in case it can't be delivered send another transaction to pay for the additional gas.  
Aside from this, Hyperlane's default hook doesn't allow any gas refunds. If the msg.value is higher than needed it's not going to be refunded.  
Users sending msg.value higher than needed are not getting refunded and they might need to pay for additional gas in a separate transaction in order to deliver their message to the destination chain.

## Recommendation
In order to solve the issues surfaced above:  
• Allow the user to pay for additional gas by using the dispatch function overload that allows specifying StandardHookMetadata.  
• Quote the dispatch fee using Mailbox.quoteDispatch(...) and refund the excess value to the user.
