### Title
Relay-fee "paid" flag counts branch execution, not actual fee value transferred - (File: contracts/Hinkal.sol)

### Summary
`_internalTransact()` guards relay compensation with a boolean `hasPaidToRelay` that is set to `true` whenever a withdrawal branch runs with a non-zero `circomData.relay`, regardless of whether the computed `relayFee` for that token is actually greater than zero. This mirrors the root cause of the Llama finding: the check counts a boolean "participation" event instead of the actual quantity/value moved, so the guarantee it is meant to enforce ("relay is paid when relay != address(0)") can be satisfied without any value reaching the relay.

### Finding Description
In `_internalTransact`: [1](#0-0) 

```
uint256 sumAbs = uint256(-deltaAmountChange);
uint256 relayFee = 0;
if (circomData.relay != address(0)) {
    uint256 flatFee = circomData.feeStructure.feeToken == circomData.erc20TokenAddresses[i]
        ? circomData.feeStructure.flatFee : 0;
    require(sumAbs >= flatFee, "Relay Fee is over withdraw amount");
    uint256 recipientAmount = ((10000 - circomData.feeStructure.variableRate) * (sumAbs - flatFee)) / 10000;
    relayFee = sumAbs - recipientAmount;
    if (relayFee > 0) {
        transferERC20TokenOrETH(circomData.erc20TokenAddresses[i], circomData.relay, relayFee);
    }
    hasPaidToRelay = true;                 // <-- set unconditionally
}
...
require(circomData.relay == address(0) || hasPaidToRelay, "relay not paid");
```

`hasPaidToRelay` is flipped to `true` the moment the `circomData.relay != address(0)` branch is entered for *any* withdrawal token, independent of whether `relayFee` computed for that iteration is non-zero. If `feeStructure.flatFee == 0` and `feeStructure.variableRate == 0` for the matching token(s) (or the token in `feeStructure.feeToken` never matches the iterated `erc20TokenAddresses[i]`), `relayFee` evaluates to `0`, no transfer to the relay ever occurs, yet the final `require(... || hasPaidToRelay)` still passes because the flag only recorded that the "relay != 0" branch executed — not that value was moved. This is the exact class of bug flagged in the external report: a guard that should assert an actual quantity (`relayFee` transferred) instead asserts participation/count (branch taken).

`feeStructure` (and thus `flatFee`/`variableRate`) is part of `CircomData` and is bound into `calldataHash` → `signedMessageHash`, so under normal operation the *user* chooses the fee structure and the relay is expected to reject unattractive (zero-fee) offers before submitting the transaction on-chain. However, the on-chain invariant itself is not "relay chose to submit a fee-bearing tx", it's coded as "relay must be paid whenever `relay != address(0)`", and that invariant is not actually enforced — it degrades to "relay address was non-zero and at least one withdrawal branch ran".

### Impact Explanation
This falls under "temporary/permanent freezing of protocol/relay fees" if the check is relied upon elsewhere as evidence that a relay was compensated (e.g., off-chain relay infra or auditing that trusts the on-chain revert as the sole enforcement mechanism). If the `hasPaidToRelay` guard is the only on-chain protection against a caller supplying a fee structure with zero effective fee, a user (potentially colluding with, or masquerading as, an authorized submitter) can submit a `transact()` call with `circomData.relay` set and a fee structure engineered to zero out `relayFee` for every negative-delta token, and the transaction still succeeds — the relay receives nothing while the check that is supposed to prevent exactly this passes silently.

### Likelihood Explanation
Low-to-medium in practice, because a rational relay will not submit a transaction whose signed fee structure yields zero fee (they control submission). The bug is real and demonstrable purely from contract logic (the flag is set without checking `relayFee > 0`), but exploiting it for actual value theft requires either (a) another actor besides the fee-entitled relay submitting the tx, or (b) the on-chain check being relied upon as the sole enforcement of payment (e.g. a permissionless relay-submission flow where the contract's revert is supposed to make non-payment impossible). Given the scope restrictions exclude "malicious relayer/node assumptions" and this exact scenario mostly benefits the withdrawer at the cost of a relay who could simply decline to relay, the concrete exploitable path is narrow.

### Recommendation
Track whether relay fee was actually greater than zero and require that the relay received non-zero value whenever `circomData.relay != address(0)` and at least one withdrawal token yields a non-zero computed fee, e.g.:
```solidity
if (relayFee > 0) {
    transferERC20TokenOrETH(...);
    hasPaidToRelay = true;
}
```
so the flag reflects an actual value transfer (the correct "quantity") rather than mere branch execution (the incorrect "count").

### Proof of Concept
1. User (or colluding submitter) constructs `circomData` with `relay = R` (non-zero), and `feeStructure = {feeToken: someToken, flatFee: 0, variableRate: 0}`.
2. Sets up one ERC20 token with negative `amountChanges` (a withdrawal) matching `feeToken == erc20TokenAddresses[i]`.
3. In `_internalTransact`, `flatFee = 0`, `recipientAmount = sumAbs`, so `relayFee = 0`; the `if (relayFee > 0)` transfer is skipped, but `hasPaidToRelay = true;` still executes because it is outside that inner `if`.
4. Final `require(circomData.relay == address(0) || hasPaidToRelay, "relay not paid")` passes even though `R` received zero tokens. [2](#0-1)

### Citations

**File:** contracts/Hinkal.sol (L172-230)
```text
    function _internalTransact(CircomData calldata circomData) private {
        bool hasPaidToRelay = false;
        for (uint64 i = 0; i < circomData.erc20TokenAddresses.length; i++) {
            int256 deltaAmountChange = _calculateDeltaAmount(circomData, i);

            if (deltaAmountChange > 0) {
                require(
                    circomData.externalActionData.externalAddress == msg.sender,
                    "Deposit should come from the sender"
                );
                transferERC20TokenFromOrCheckETH(
                    circomData.erc20TokenAddresses[i],
                    circomData.externalActionData.externalAddress,
                    address(this),
                    uint256(circomData.amountChanges[i])
                );
            } else {
                uint256 sumAbs = uint256(-deltaAmountChange);
                uint256 relayFee = 0;
                if (circomData.relay != address(0)) {
                    uint256 flatFee = circomData.feeStructure.feeToken ==
                        circomData.erc20TokenAddresses[i]
                        ? circomData.feeStructure.flatFee
                        : 0;

                    require(
                        sumAbs >= flatFee,
                        "Relay Fee is over withdraw amount"
                    );

                    uint256 recipientAmount = ((10000 -
                        circomData.feeStructure.variableRate) *
                        (sumAbs - flatFee)) / 10000;

                    relayFee = sumAbs - recipientAmount;

                    if (relayFee > 0) {
                        transferERC20TokenOrETH(
                            circomData.erc20TokenAddresses[i],
                            circomData.relay,
                            relayFee
                        );
                    }
                    hasPaidToRelay = true;
                }
                if (sumAbs - relayFee > 0) {
                    transferERC20TokenOrETH(
                        circomData.erc20TokenAddresses[i],
                        circomData.externalActionData.externalAddress,
                        sumAbs - relayFee
                    );
                }
            }
        }
        require(
            circomData.relay == address(0) || hasPaidToRelay,
            "relay not paid"
        );
    }
```
