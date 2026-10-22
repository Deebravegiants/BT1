# [H] Anyone can overwrite Reputer

## Summary
Severity: High
Contest weight: 0.3792
Dataset id: 23047
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The allora-chain does not verify that the caller owns the LibP2PKey. This allows anyone to modify the reputers and/or workers informations for a given key.
The Register message allows to register as a reputer or as a worker or as both (require 2 calls).
When a reputer is registered, an entry is added into k.reputers to map a LibP2PKey to reputer infos.
However, there are no checks to ensure that the provided LibP2PKey is owned by the caller. Moreover, if an existing entry exist for this LibP2PKey, it is overwritten.
The same applies to the worker
Anyone can overwrite the Owner attached to a LibP2PKey for reputers and workers.
This is highly problematic because these data are retrieved in the allora-inference-base codebase.
Issue
The Register entrypoint takes the entry parameters and calls InsertReputer.
See msg_server_registrations.go#L41-L53.
// Registers a new network participant to the network for the first time for worker or reputer
func (ms msgServer) Register(ctx context.Context, msg *types.MsgRegister)
nodeInfo := types.OffchainNode{
NodeAddress: msg.Sender,
LibP2PKey: msg.LibP2PKey,
MultiAddress: msg.MultiAddress,
Owner: msg.Owner,
NodeId: msg.Owner + "|" + msg.LibP2PKey,
}
if msg.IsReputer {
err = ms.k.InsertReputer(ctx, msg.TopicId, msg.Sender, nodeInfo) // @POC: Register node info
if err != nil {
return nil, err
}
} else {
//...
}
}
InsertReputer will not check if an existing entry exist for the given LibP2PKey and will overwrite it via Set. It will write to k.reputers.
See keeper.go#L124-L125 and keeper.go#L1432-L1443.
type Keeper {
// map of reputer id to node data about that reputer
reputers collections.Map[LibP2pKey, types.OffchainNode] // @POC: Map a `LibP2pKey` to node info
}
// Adds a new reputer to the reputer tracking data structures, reputers and topicReputers
func (k *Keeper) InsertReputer(ctx context.Context, topicId TopicId, reputer ActorId, reputerInfo types.OffchainNode) error {
topicKey := collections.Join(topicId, reputer)
err := k.topicReputers.Set(ctx, topicKey)
if err != nil {
return err
}
err = k.reputers.Set(ctx, reputerInfo.LibP2PKey, reputerInfo) // @POC: adds OR MODIFY an entry in `k.reputers`
if err != nil {
return err
}
return nil
}
allora-chain provides a query entrypoint to retrieve the reputer informations by providing the LibP2PKey. This entrypoint is GetReputerAddressByP2PKey. (See query_server_registrations.go#L37-L44 and keeper.go#L1503-L1504).
// query_server_registrations.go#L37-L44
func (qs queryServer) GetReputerAddressByP2PKey(ctx context.Context, req *types.QueryReputerAddressByP2PKeyRequest)
address, err := qs.k.GetReputerAddressByP2PKey(sdk.UnwrapSDKContext(ctx), req.Libp2PKey)
if err != nil {
return nil, err
}
nil
}
// keeper.go#L1503-L1504
func (k *Keeper) GetReputerAddressByP2PKey(ctx context.Context, p2pKey string) (sdk.AccAddress, error) {
reputer, err := k.reputers.Get(ctx, p2pKey) // @POC: retrieves the entry that anyone can overwrite
}
The allora-inference-base codebase retrieves reputer informations by calling GetReputerAddressByP2PKey on allora-chain. (See appchain.go#L545-L548)
// Sending Losses to the AppChain
func (ap *AppChain) SendReputerModeData(ctx context.Context, topicId uint64, results aggregate.Results) {
// Get Peer $allo address
res, err := ap.EmissionsQueryClient.GetReputerAddressByP2PKey(ctx, &emissionstypes.QueryReputerAddressByP2PKeyRequest{ // @POC: retrieves data from allora-chain
Libp2PKey: peer.String(),
})
To summarize, an attacker can modify infos attached to any LibP2PKey to poison the allora-inference-base and break the Allora network.
Worker snippets
The given code snippets affect the reputer registration. However, the worker registration shows similar issue.
Here are the snippet links for the worker registration:
• entrypoint at msg_server_registrations.go#L54-L59
• at keeper.go#L1461-L1473
• at query_server_registrations.go#L28-L35
• at keeper.go#L1489-L1501
Then allora-inference-base retrieves info for workers:
• appchain.go#L339

## Recommendation
Allora-chain should verify that the provided key is owned by the caller.
The most efficient way to handle this issue seems to require the signature of the Msg.Owner
