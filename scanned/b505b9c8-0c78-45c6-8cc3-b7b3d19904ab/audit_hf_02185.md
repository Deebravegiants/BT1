# [H] Incomplete Genesis State For Future Upgrades

## Summary
Severity: High
Contest weight: 0.3750
Dataset id: 12180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
HBTC Chain is developed on top of Cosmos-SDK[7], a popular modular framework for building application-specific blockchains. Note that Cosmos-SDK enables rapid development of SDK-based blockchains out of composable modules. HBTC Chain leverages some existing modules (with its own customization) and further develops unique ones for the purpose of digital asset custody and clearing. Speciﬁcally, cu provides a custody unit for asset management, token enlists available tokens for trading or custody, mapping supports cross-chain asset mapping, keygen provides dynamic key generation services for cross-chain assets, and hrc20 enables ERC20-like token issuance and transfer primitives on HBTC Chain etc. The modular Cosmos-SDK framework allows various modules to generally handle a subset of the state and, as such, these modules need to define the related subset of the genesis file as well as methods to initialize, verify, and export it. We stress that these states are essential to the blockchain's genesis state import and export and are therefore required for seamless upgrades. In the current HBTC Chain codebase, several modules do not have thorough genesis-related states properly exported or imported. Consequently, they could lead to broken upgrades. Using the custodianunit (a.k.a., cu) module as an example, we show below the implementation of current InitGenesis and ExportGenesis routines. As the names indicate, they are executed whenever an import or export of the state is made. The ExportGenesis routine exported both params and cus, but the InitGenesis routine only imported params, not cus. In other words, all created cus in a previous run may be lost for a resumed run of HBTC Chain after upgrade.
```go
// InitGenesis - Init store state from genesis data
// CONTRACT: old coins from the FeeCollectionKeeper need to be transferred through
// a genesis port script to the new fee collector
func InitGenesis(ctx sdk.Context, ak CUKeeper, data GenesisState) {
    ak.SetParams(ctx, data.Params)
}

// ExportGenesis returns a GenesisState for a given context and keeper
func ExportGenesis(ctx sdk.Context, ck CUKeeper) GenesisState {
    params := ck.GetParams(ctx)
    cus := ck.GetAllCUs(ctx)
    return NewGenesisState(params, cus)
}
```
Incomplete, without the validation of saved cus in the genesis state.
```go
// ValidateGenesis performs basic validation of auth genesis data returning
// error for any failed validation criteria.
func ValidateGenesis(data GenesisState) error {
    if data.Params.TxSigLimit == 0 {
        return fmt.Errorf("invalid signature limit: %d", data.Params.TxSigLimit)
    }
    if data.Params.SigVerifyCostED25519 == 0 {
        return fmt.Errorf("invalid ED25519 signature verification cost: %d", data.Params.SigVerifyCostED25519)
    }
    if data.Params.SigVerifyCostSecp256k1 == 0 {
        return fmt.Errorf("invalid SECK256k1 signature verification cost: %d", data.Params.SigVerifyCostSecp256k1)
    }
    if data.Params.MaxMemoCharacters == 0 {
        return fmt.Errorf("invalid max memo characters: %d", data.Params.MaxMemoCharacters)
    }
    if data.Params.TxSizeCostPerByte == 0 {
        return fmt.Errorf("invalid tx size cost per byte: %d", data.Params.TxSizeCostPerByte)
    }
    return nil
}
```
transfer, and keygen. And their individual routines in (InitGenesis, ExportGenesis, and ValidateGenesis) also need to be revised accordingly.

## Recommendation
Appropriately import and export necessary genesis state in affected modules.
