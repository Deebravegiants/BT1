# [M] Lack of Authentication in On-

## Summary
Severity: Medium
Contest weight: 0.2474
Dataset id: 23050
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Axelar sample code acknowledges the importance of authenticating the message based on the channel ID, in addition to verifying the packet sender. However, the Allora chain's implementation does not include any channel ID/sender authentication logic.
In the provided code for the Allora chain's IBC middleware (gmp/middleware.go), the OnRecvPacket function does not perform authentication based on the channel ID when processing incoming packets. This can potentially lead to security vulnerabilities and allow unauthorized or unintended processing of packets.
Comparing it with the Axelar sample code (gmp_middleware/middleware.go), there is a
// TODO: authenticate the message with channel-id
if data.Sender != AxelarGMPAcc {
return ack
}
Without verifying the channel ID, the middleware may process packets from unintended or unauthorized channels. This can result in the execution of malicious or unexpected actions on the receiving chain.
Axelar Sample : https://github.com/axelarnetwork/evm-cosmos-gmp-sample/blob/main/native-integration/sample-middleware/gmp_middleware.go#L114
ibc_middleware.go#L112-L113
// OnRecvPacket implements the IBCMiddleware interface
func (im IBCMiddleware) OnRecvPacket(
ctx sdk.Context,
packet channeltypes.Packet,
relayer sdk.AccAddress,
) ibcexported.Acknowledgement {
var data transfertypes.FungibleTokenPacketData
if err := transfertypes.ModuleCdc.UnmarshalJSON(packet.GetData(), &data); err != nil {
return channeltypes.NewErrorAcknowledgement(fmt.Errorf("cannot unmarshal ICS-20 transfer packet data"))
}
var msg Message
var err error
err = json.Unmarshal([]byte(data.GetMemo()), &msg)
if err != nil || len(msg.Payload) == 0 {
// Not a packet that should be handled by the GMP middleware
return im.app.OnRecvPacket(ctx, packet, relayer)
}
//if !strings.EqualFold(data.Sender, AxelarGMPAcc) {
//
// Not a packet that should be handled by the GMP middleware
//
return im.app.OnRecvPacket(ctx, packet, relayer)
//}
logger := ctx.Logger().With("handler", "GMP")
switch msg.Type {
case TypeGeneralMessage:
logger.Info("Received TypeGeneralMessage",
"srcChain", msg.SourceChain,
"srcAddress", msg.SourceAddress,
"receiver", data.Receiver,
"payload", string(msg.Payload),
"handler", "GMP",
)
// let the next layer deal with this
// the rest of the data fields should be normal
fallthrough
case TypeGeneralMessageWithToken:
logger.Info("Received TypeGeneralMessageWithToken",
"srcChain", msg.SourceChain,
"srcAddress", msg.SourceAddress,
"receiver", data.Receiver,
"payload", string(msg.Payload),
"coin", data.Denom,
"amount", data.Amount,
"handler", "GMP",
)
// we throw out the rest of the msg.Payload fields here, for better or worse
data.Memo = string(msg.Payload)
var dataBytes []byte
if dataBytes, err = transfertypes.ModuleCdc.MarshalJSON(&data); err != nil {
return channeltypes.NewErrorAcknowledgement(fmt.Errorf("cannot marshal ICS-20 post-processed transfer packet data"))
}
packet.Data = dataBytes
return im.app.OnRecvPacket(ctx, packet, relayer)
default:
return channeltypes.NewErrorAcknowledgement(fmt.Errorf("unrecognized mesasge type: %d", msg.Type))
}
}

## Recommendation
Modify the OnRecvPacket function to include a check that verifies the authenticity of the packet based on the channel ID/sender.
