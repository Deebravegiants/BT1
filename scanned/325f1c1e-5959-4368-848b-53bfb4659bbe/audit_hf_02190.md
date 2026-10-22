# [M] Inappropriate Initialization Order of Modules

## Summary
Severity: Medium
Contest weight: 0.6062
Dataset id: 12187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The various composable modules in HBTC Chain have their own internal dependencies that need to be honored during initialization and tear-down. For example, the module genutils must occur after staking so that pools are properly initialized with tokens from genesis accounts. Also, capability module, if present, must occur ﬁrst so that it can initialize any capabilities so that other modules that want to create or claim capabilities afterwards can do so safely. Similarly, gov and slashing depend on bank for accessing and/or modifying balances.
```solidity
// During begin block slashing happens after distr. BeginBlocker so that
// there is nothing left over in the validator fee pool, so as to keep the CanWithdrawInvariant invariant.
app.mm.SetOrderBeginBlockers(mint.ModuleName, distr.ModuleName, slashing.ModuleName)
app.mm.SetOrderEndBlockers(crisis.ModuleName, gov.ModuleName, staking.ModuleName)
// NOTE: The genutils moodule must occur after staking so that pools are properly initialized with tokens from genesis accounts.
app.mm.SetOrderInitGenesis(
    genaccounts.ModuleName, otypes.ModuleName, receipt.ModuleName, token.ModuleName,
    keygen.ModuleName, distr.ModuleName, staking.ModuleName, custodianunit.ModuleName,
    transfer.ModuleName, slashing.ModuleName, gov.ModuleName, mint.ModuleName,
    supply.ModuleName, crisis.ModuleName, genutil.ModuleName, hrc20.ModuleName,
    mapping.ModuleName,
)
```
In particular, the app.mm.SetOrderInitGenesis() indicates the InitGenesis order that needs to satisfy inherent dependency. In Figure 3.1, we outline the actual dependency among current modules in HBTC Chain. The actual dependency is derived by examining the related inter-module keeper references in each module. In other words, if a module, say keygen, references order, we can infer keygen depends on order, hence order -> keygen in the dependency ﬁgure.
Public
token transfer keygen hrc20 mapping genaccounts supply order receipt params staking mint distr slashing genutil crisis gov
Figure 3.1: The Module Dependency in HBTC Chain
By cross-checking app.mm.SetOrderInitGenesis with the above dependency ﬁgure, we obtain the following possible violations of module dependency: keygen, distr, staking, cu, transfer, gov, mint, and supply. An inappropriate order may cause broken initialization or introduce wrong runtime state and thus need to be certainly avoided.

## Recommendation
The relevant ﬁxup is rather straightforward. Basically, we need to apply the module initialization in the order by following their inherent dependency.
```solidity
// NOTE: The genutils moodule must occur after staking so that pools are properly initialized with tokens from genesis accounts.
app.mm.SetOrderInitGenesis(
/* Old Order
genaccounts.ModuleName , otypes.ModuleName , receipt.ModuleName , token.ModuleName ,
keygen.ModuleName , distr.ModuleName , staking.ModuleName ,
custodianunit .ModuleName , transfer.ModuleName , slashing.ModuleName , gov.
ModuleName ,
mint.ModuleName , supply.ModuleName , crisis.ModuleName , genutil.ModuleName , hrc20
.ModuleName ,
mapping.ModuleName ,
// New Order
otypes.ModuleName,
receipt.ModuleName,
token.ModuleName,
Public
custodianunit.ModuleName,
genaccounts.ModuleName,
supply.ModuleName,
gov.ModuleName,
staking.ModuleName,
crisis.ModuleName,
slashing.ModuleName,
genutil.ModuleName,
mint.ModuleName,
distr.ModuleName,
transfer.ModuleName,
keygen.ModuleName,
hrc20.ModuleName,
mapping.ModuleName,
```
