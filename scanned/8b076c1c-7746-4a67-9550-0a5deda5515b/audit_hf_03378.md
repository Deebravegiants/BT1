# [H] Some offers can’t be cancelled

## Summary
Severity: High
Contest weight: 0.4205
Dataset id: 18444
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an inability for a regular user to cancel an offer that was created through the SimpleMarket API. The root cause is that the SimpleMarket contract inherits from RubiconMarket but does not override the `offer` function, so the implementation that inserts a newly created offer into the internal linked‑list structures (`_rank` and `_near`) is never executed. When a user creates an offer via SimpleMarket, the offer is recorded only in a minimal storage slot and never added to the sorted ranking list that the cancel logic expects. Later, when the user calls the `cancel` function (which is overridden in RubiconMarket), the cancel routine checks two conditions: `isOfferSorted` – which verifies that the offer appears in `_rank` – and `_hide` – which verifies that the offer is present in the unsorted list `_near`. Because the offer was never inserted into either list, both checks return false and the require statement in `_hide` reverts the transaction. Consequently the user cannot cancel the order, the funds remain locked, and the market’s accounting becomes inconsistent. This situation occurs only when the offer is created through the SimpleMarket interface; offers created directly via RubiconMarket can be cancelled normally. The affected parties are ordinary market participants who rely on the SimpleMarket API, as well as the protocol itself because stuck offers can distort liquidity and price discovery. The issue was discovered during a code audit and reproduced with a test that called SimpleMarket’s `offer` followed by RubiconMarket’s `cancel`, which consistently reverted. It is hard to notice because the UI may show the order as active and the cancel button may appear functional, yet the transaction fails with a generic revert, giving no clear indication that the problem lies in the contract inheritance. The bug belongs to the class of inheritance‑related state‑inconsistency errors, where a derived contract fails to forward a call to the correct implementation, leading to mismatched internal state. From a user’s perspective the expectation is that an order can be withdrawn at any time; instead the transaction reverts and the user sees no refund, effectively losing access to the locked funds. To remediate the issue the SimpleMarket contract should explicitly override the `offer` function and delegate to RubiconMarket’s full `offer` implementation, ensuring that every new offer is correctly inserted into `_rank` and `_near`. This alignment restores the invariant that every active offer is tracked by the cancel logic, allowing users to cancel and retrieve their assets as intended.

## Proof of Concept
1. The function [`offer`](https://github.com/code-423n4/2023-04-rubicon/blob/main/contracts/RubiconMarket.sol#L511) of `SimpleMarket` is not overridden by the `RubiconMarket` contract. _Note: that this function is called in the testing[example](https://github.com/code-423n4/2023-04-rubicon/blob/main/test/foundry-tests/ProtocolDeployment.t.sol#L89)_
  2. The [`cancel`](https://github.com/code-423n4/2023-04-rubicon/blob/main/contracts/RubiconMarket.sol#L452) function inside `SimpleMarket` is overridden by the [`cancel`](https://github.com/code-423n4/2023-04-rubicon/blob/main/contracts/RubiconMarket.sol#L871) function in `RubiconMarket`.

When a normal user creates an offer with the `SimpleMarket` API(1), the offer is not inserted into the linked list `_rank`.

After some time the user wants to cancel their order. They can only call `RubiconMarket`’s `cancel` function(2). When they call `cancel` what will happen is:

  1. [`isOfferSorted`](https://github.com/code-423n4/2023-04-rubicon/blob/main/contracts/RubiconMarket.sol#L876) will return `false` because the offer was never inserted into `_rank`.
  2. [`_hide`](https://github.com/code-423n4/2023-04-rubicon/blob/main/contracts/RubiconMarket.sol#L879) will also return `false`, Because the offer was not inserted into the unsorted list `_near`.
  3. Require check will fail because `_hide` returned `false`.

Therefore, the user won’t be able to cancel their offer.

## Recommendation
Override the `offer` function in `SimpleMarket` with the `offer` function in `RubiconMarket`. Add this offer function:
    
    function offer(
        uint256 pay_amt,
        ERC20 pay_gem,
        uint256 buy_amt,
        ERC20 buy_gem,
        address owner,
        address recipient
    ) public override can_offer returns (uint256) {
        return
            offer(
                pay_amt,
                pay_gem,
                buy_amt,
                buy_gem,
                0,
                true,
                owner,
                recipient
            );
      }
