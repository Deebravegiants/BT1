# [M] Multiple initialization in `NoteInterest`

## Summary
Severity: Medium
Contest weight: 0.4240
Dataset id: 9981
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The NoteInterest contract contains an initialization function that can be invoked repeatedly by the admin address. The vulnerability is a classic re‑initialization bug: the contract does not keep any state flag indicating whether it has already been set up, nor does it use a standard initializer guard such as OpenZeppelin’s Initializable pattern. Because of this omission, the function can be called an arbitrary number of times after deployment, each call overwriting the stored cNote token reference and the price oracle address that the interest‑calculation model relies on. The root cause is the missing require statement that would reject subsequent calls once the contract has been initialized. An attacker who gains control of the admin role—or a malicious governance proposal—can exploit this by calling initialize with a malicious oracle or a different cNote address. By swapping the oracle, the attacker can feed false price data, causing the updateBaseRate logic to compute an incorrect base rate, potentially driving the interest rate to zero, to an extreme value, or to a value that redirects accrued interest to an address under the attacker’s control. Changing the cNote address could also redirect token interactions to a contract that does not hold user balances, making user balances appear empty after transactions. The impact is that users may see their interest rewards disappear, their token balances become zero, or the protocol’s accounting invariants break, leading to loss of funds under specific but realistic conditions. The vulnerability manifests whenever the admin calls initialize after the contract has already been set up; there is no temporal restriction preventing repeated calls. All participants who rely on the correctness of the interest calculation—depositors, borrowers, and the protocol itself—are affected. The issue was discovered during a Code4rena audit when the warden highlighted that the initialize function lacks any protection against multiple invocations. It can be hard to notice because the function appears as a normal administrative setter, and the UI typically does not surface a warning when the parameters change, so users may only observe unexpected behavior such as zero interest payouts or missing balances. To remediate, the contract should introduce an immutable initialization flag that is set to true on the first successful call and disallows further calls, or it should move the setup logic into the constructor. Using a well‑tested initialization pattern from a trusted library (e.g., OpenZeppelin’s Initializable) would also ensure the contract adheres to the business logic that the token address and price oracle remain constant after deployment, preserving the protocol’s accounting guarantees.

## Proof of Concept
The method `initialize` of the contract `NoteInterest` looks like this:

```solidity
function initialize(address cnoteAddr, address oracleAddress) external {
    if (msg.sender != admin) {
        revert SenderNotAdmin(msg.sender);
    }   
    address oldPriceOracle = address(oracle);
    cNote = CErc20(cnoteAddr);
    oracle = PriceOracle(oracleAddress);
    emit NewPriceOracle(oldPriceOracle, oracleAddress);
}
```

Nothing prevents it from being initialized again and altering the initial values of the contract. This allows the government, unnecessarily, to be able to perform attacks such as altering the logic of the `updateBaseRate` method.

## Recommendation
Add a require to check that was not already initialized.

It is not clear how governance would be able to modify the logic in updateBaseRate? All that could be changed is the price oracle that the NoteInterest Model references.

The warden has shown that the function `initialize` can be called multiple times by governance.

This could cause undefined behaviour (e.g. change the token address), which could cause loss of funds.

Because of the system setup, it would be best to make sure that `initialize` can only be called once.

Because the finding can cause a loss, under specific circumstances, I believe Medium Severity is appropriate
