# [M] Missing export CoreTeamAddres

## Summary
Severity: Medium
Contest weight: 0.1117
Dataset id: 23073
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
module
The genesis state of x/emissions module is defined below:
allora-chain/x/emissions/types/genesis.pb.go
type GenesisState struct {
// params defines all the parameters of the module.
Params Params `protobuf:"bytes,1,opt,name=params,proto3" json:"params"`
}
missing.
func (k *Keeper) ExportGenesis(ctx context.Context) (*types.GenesisState, error) {
moduleParams, err := k.GetParams(ctx)
if err != nil {
return nil, err
}
return &types.GenesisState{
Params: moduleParams,
}, nil
}
upgrade. Thus, all the whitelist admin-related functions will be blocked, such as adding a new admin member or updating the module parameters.
All the whitelist admin-related functions will be blocked, such as adding a new admin member or updating the module parameters.

## Recommendation
No recommendation available
