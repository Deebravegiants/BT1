# [M] `SwingTraderManager.swingTraders

## Summary
Severity: Medium
Contest weight: 0.4566
Dataset id: 18138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a duplicate‑entry flaw in the SwingTraderManager contract where the mapping that stores swing trader data does not enforce that each traderContract address is unique. When an administrator calls addSwingTrader, the function only checks that the traderId is unused and that the address is non‑zero, but it never verifies that the supplied _swingTrader address has not already been registered under a different traderId. As a result the same external trader contract can be associated with multiple trader identifiers. This double‑counting corrupts the accounting logic used by functions such as buyMalt and sellMalt, which allocate Malt tokens proportionally to each trader’s recorded balance. Because the protocol believes there are two separate traders when in fact there is only one, the shared contract receives a larger share of the distribution than it can actually manage, leading to an over‑allocation of tokens, incorrect share ratios, and potentially lost or unaccounted funds. The issue manifests whenever an admin adds a new swing trader without a uniqueness guard; it is triggered at the moment of addition and persists until the duplicate entries are removed. Users of the protocol are affected because they expect to receive a correct amount of Malt when buying or selling through a swing trader, but they may see their balances become unexpectedly high or low, or see refunds that do not match the expected amount. From a UI perspective a user might notice that a particular trader shows up twice in a list, or that the total allocated Malt does not match the sum of individual balances, leading to confusion and mistrust. The flaw was discovered during a manual audit by Code4rena, which highlighted the lack of a uniqueness check as a logical oversight. It can be hard to notice because the contract does not revert or emit an explicit error; the incorrect distribution only becomes apparent when aggregated totals are examined or when a trader contract cannot honor the excess shares it has been assigned. To remediate the problem, the contract should maintain a secondary mapping (for example activeTraderContracts) that records whether a traderContract address has already been registered, and the addSwingTrader function should require that the address is not already present before inserting a new entry. This ensures each external trader contract is represented exactly once, preserving the integrity of balance calculations and preventing double‑counting bugs that break the protocol’s accounting assumptions.

## Proof of Concept
During the swing trader addition, there is no validation that each trader should have a unique `traderContract`.

```solidity
function addSwingTrader(
  uint256 traderId,
  address _swingTrader, // @audit should be unique
  bool active,
  string calldata name
) external onlyRoleMalt(ADMIN_ROLE, "Must have admin privs") {
  SwingTraderData storage trader = swingTraders[traderId];
  require(traderId > 2 && trader.id == 0, "TraderId already used");
  require(_swingTrader != address(0), "addr(0)");

  swingTraders[traderId] = SwingTraderData({
    id: traderId,
    index: activeTraders.length,
    traderContract: _swingTrader,
    name: name,
    active: active
  });

  activeTraders.push(traderId);

  emit AddSwingTrader(traderId, name, active, _swingTrader);
}
```

So the same `traderContract` might have 2 or more `traderId`s.

When we check `buyMalt()` as an example, it distributes the ratio according to the trader balance and it wouldn’t work properly if one trader contract is counted twice and receives more shares that it can’t manage.

Similarly, other functions wouldn’t work as expected and return the wrong result.

## Recommendation
Recommend adding a new mapping like `activeTraderContracts` to check if the contract is added already or not.

Then we can check the trader contract is added only once.
