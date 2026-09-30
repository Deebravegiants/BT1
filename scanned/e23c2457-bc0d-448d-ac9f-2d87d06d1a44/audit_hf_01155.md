# [H] Unbounded swap path parameter vulnerability enabling node Denial of Service attacks

## Summary
Severity: High
Reporter: metaldragon, also found by WaﬄeWizard and Skylice
Contest weight: 0.7871
Dataset id: 4928
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The decentralized exchange module enables users to provide custom swap paths
without implementing proper size limitations, creating a vulnerability where attackers can overwhelm
node resources by submitting excessively long and repetitive swap paths, as the blockchain lacks na-
tive resource consumption constraints. The exchange functionality allows users to execute token swaps
through established pair liquidity pools via two primary operations:
• swap_exact_tokens_for_tokens.
• swap_tokens_for_exact_tokens.
Both operations accept a user-deﬁned path parameter that speciﬁes the sequence of token pairs for
routing the swap transaction (e.g., TokenA/TokenB →TokenB/TokenC →TokenC/TokenD). Depending on
which function is invoked, users specify either the input amount or desired output amount. Since both
operations follow similar execution patterns requiring comparable database interactions, we'll focus on
one example. After receiving the amount_in in the swap_exact_tokens_for_tokens operation, the system
calculates expected outputs using the get_amounts_out function:
```solidity
val amounts_response = get_amounts_out(amount_in, from_assets_symbol_to_assets(path));
```
Before performing calculations, the system resolves token symbols to actual asset records through
database queries:
```solidity
function from_assets_symbol_to_assets(assets_symbol: list<text>): list<asset> {
    val assets: list<asset> = [];
    for (asset_symbol in assets_symbol) {
        val asset_finding = asset @? { .symbol == asset_symbol };
        if (asset_finding != null) {
            assets.add(asset_finding);
        } else {
        }
    }
    return assets;
}
```
This creates a separate database SELECT query for each token symbol in the provided path. The get_-
amounts_out function then queries for each pair in the path to retrieve their reserves:
```solidity
for (i in range(path.size()-1)) {
    val (
        input_reserve,
        output_reserve
    ) = get_reserves_for_token(
        get_force_pair(
            path[i],
            path[i + 1]
        ),
        path[i],
        path[i + 1]
    );
    val get_amount_response = get_amount_out(old_amount, input_reserve, output_reserve);
    amounts_response.add(get_amount_response);
    old_amount = get_amount_response.amount_out;
}
```
This generates (N −1) additional queries for pair retrieval plus computational overhead for each calcu-
lation. After calculations are completed, the entire process repeats during execution. Within the _swap
function, the system processes each pair sequentially, retrieving pair data, executing swaps, and creating
transaction history records:
```solidity
function _swap(amounts_response: list<get_amount_response>, path: list<asset>, to_user_account: account) {
    var to = to_user_account;
    for (i in range(path.size()-1)) {
        val input = path[i];
        val output = path[i + 1];
        val (token0, _) = sort_asset(input, output);
        // [calculation logic]
        if (i < path.size() - 2) {
            to = get_force_pair(output, path[i + 2]).treasury;
        } else {
            to = to_user_account;
        }
        swap(get_force_pair(input, output), amount0_out, fee_0_out, amount1_out, fee_1_out, to);
        create uniswap_history_transaction (
            // [transaction record creation]
        );
    }
}
```
This generates (N −1) SELECT operations and (N −1) INSERT operations, consuming substantial resources.
While normal usage scenarios wouldn't cause performance issues, the critical vulnerability lies in the ab-
sence of path size limitations or validation against repeating tokens. With no gas mechanism to constrain
computations, attackers can submit abnormally large paths with repeating tokens, forcing nodes to per-
form excessive calculations and database operations while consuming no more user credit than a stan-
dard swap would require.

Impact Explanation:
High impact due to potential node paralysis with minimal attacker resources, af-
fecting availability of the entire blockchain system.

## Recommendation
Implement strict path length limits (5-10 hops maximum), prevent cyclic paths, and
add validation against repeating tokens in all swap operations and related query functions.
3.2
