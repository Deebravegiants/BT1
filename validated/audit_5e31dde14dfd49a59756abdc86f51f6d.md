I need to carefully trace the treasury withdrawal accounting logic in the Conway era to determine if an analog to the overcommitment vulnerability exists.

**Vulnerability class:** Funds/accounting bug — a global balance variable is checked but not decremented at the reservation step, allowing multiple actors to overcommit the same funds.

**Mapping to Cardano Ledger:** The analog candidate is the `ensTreasury` field in `EnactState`, which tracks the treasury balance during ratification of `TreasuryWithdrawals` governance proposals.