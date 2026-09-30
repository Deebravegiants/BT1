# [M] logic bug in this IBC middle

## Summary
Severity: Medium
Contest weight: 0.4414
Dataset id: 23063
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the OnRecvPacket function, the code attempts to parse the packet's memo field into a custom Message structure. However, the logic for determining whether the middleware should process the packet or pass it to the next layer is flawed.
The Flawed Logic
//if !strings.EqualFold(data.Sender, AxelarGMPAcc) {
//
// Not a packet that should be handled by the GMP middleware
//
return im.app.OnRecvPacket(ctx, packet, relayer)
//}
This suggests an intention to filter packets based on the sender's address. However, even without this check, the code falls through to process the packet if the memo can be unmarshalled into a Message with a non-empty payload.
The Consequence
This means that the GMP middleware might unintentionally process packets that were not meant for it, potentially leading to unexpected behavior or errors further down the line.
The Solution
we should reintroduce the sender address check or different check before deciding to process the packet. example
// ... (other parts of the code remain the same)
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
if !strings.EqualFold(data.Sender, AxelarGMPAcc) { // <-- Reintroduced check
// Not a packet that should be handled by the GMP middleware
return im.app.OnRecvPacket(ctx, packet, relayer)
}
// ... (rest of the packet processing logic) ...
}
// ... (other parts of the code remain the same)
Key Points:
• By adding the check !strings.EqualFold(data.Sender,AxelarGMPAcc), the middleware will only process packets that have the expected sender address (AxelarGMPAcc).
• If the sender address doesn't match or there's an issue with the memo, the packet is passed to the next layer via im.app.OnRecvPacket(ctx,packet,relayer).
• This ensures that the GMP middleware operates on the intended packets only, preventing potential processing errors and maintaining the integrity of the IBC message flow.

## Proof of Concept
package main
import (
"encoding/json"
"fmt"
"github.com/cosmos/cosmos-sdk/types"
transfertypes "github.com/cosmos/ibc-go/v8/modules/apps/transfer/types"
channeltypes "github.com/cosmos/ibc-go/v8/modules/core/04-channel/types"
ibcexported "github.com/cosmos/ibc-go/v8/modules/core/exported"
)
// Simulate the Message struct from your code
type Message struct {
Type int `json:"type"`
Payload string `json:"payload"`
SourceChain string `json:"srcChain"`
SourceAddress string `json:"srcAddress"`
}
// Simulate the IBCMiddleware struct
type IBCMiddleware struct{}
// Simulate the next layer's OnRecvPacket function
func (im IBCMiddleware) appOnRecvPacket(ctx types.Context, packet channeltypes.Packet, relayer types.AccAddress) ibcexported.Acknowledgement {
fmt.Println("Packet received and processed by the next layer:", packet)
return channeltypes.NewResultAcknowledgement([]byte("success"))
}
// OnRecvPacket function with the logical flaw
func (im IBCMiddleware) OnRecvPacket(
ctx types.Context,
packet channeltypes.Packet,
relayer types.AccAddress,
) ibcexported.Acknowledgement {
var data transfertypes.FungibleTokenPacketData
json.Unmarshal(packet.GetData(), &data)
var msg Message
json.Unmarshal([]byte(data.GetMemo()), &msg)
if len(msg.Payload) != 0 { // Flawed condition: only checks for non-empty payload
fmt.Println("GMP middleware processing packet:", packet)
// ... further processing ...
}
// Falls through to the next layer even if not intended for GMP
return im.appOnRecvPacket(ctx, packet, relayer)
}
func main() {
// Simulate a packet not intended for GMP (wrong sender)
packetData := transfertypes.FungibleTokenPacketData{
Sender: "cosmos1wrongsender",
Receiver: "cosmos1receiver",
Amount: "100",
Denom: "uatom",
Memo: `{"type":1, "payload":"some data"}`, // Valid memo
}
packetBytes, _ := json.Marshal(packetData)
packet := channeltypes.Packet{
Data: packetBytes,
}
middleware := IBCMiddleware{}
middleware.OnRecvPacket(types.Context{}, packet, types.AccAddress{})
}
Explanation
1. We create simplified versions of Message, IBCMiddleware, and the next layer's OnRecvPacket.
2. OnRecvPacket: The function only checks if the msg.Payload is non-empty. Even though the sender is incorrect, the packet will be processed by the GMP middleware due to the valid memo.
3. We create a packet with a valid memo but an incorrect sender ("cosmos1wrongsender"). 4 When the middleware receives this packet, it incorrectly assumes it's meant for GMP and proceeds with further processing.
Output
we should see output similar to this:
GMP middleware processing packet: {"data":"eyJTZW5kZXIiOiJjb3Ntb3Mxcm9uZ3NlbmRlciIsIlJlY2VpdmVyIjoiY29zbW9zMXJlY2VpdmVyIiwiQW1vdW50IjoiMTAwIiwiRGVub20iOiJ1YXRvbSIsIk1lbW8iOnsieXR5cGUiOjEsInBheWxvYWQiOiJzb21lIGRhdGEifX0=","timeout_height":"0-0","timeout_timestamp":0}
Packet received and processed by the next layer: {"data":"eyJTZW5kZXIiOiJjb3Ntb3Mxcm9uZ3NlbmRlciIsIlJlY2VpdmVyIjoiY29zbW9zMXJlY2VpdmVyIiwiQW1vdW50IjoiMTAwIiwiRGVub20iOiJ1YXRvbSIsIk1lbW8iOnsieXR5cGUiOjEsInBheWxvYWQiOiJzb21lIGRhdGEifX0=","timeout_height":"0-0","timeout_timestamp":0}
Key Takeaways
• This PoC clearly shows the GMP middleware processing a packet that shouldn't have been intended for it.
check to ensure the middleware operates on the correct set of packets.

## Recommendation
No recommendation available
