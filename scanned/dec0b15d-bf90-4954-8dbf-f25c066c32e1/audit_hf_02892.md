# [C] UBT-1 | Stuck ETH Funds

## Summary
Severity: Critical
Contest weight: 0.0605
Dataset id: 16193
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a permanent lock‑up of native Ether that is transferred to the protocol treasury. When the EmergencySafeWithdraw function of a dependent contract such as SquidBetPrizePool is invoked, it forwards Ether to the treasury address, but the treasury contract does not implement any mechanism to move that Ether out, to convert it into the designated funding token, or to allocate it for further use. The root cause is a missing withdrawal or conversion routine in the treasury’s code, which means the contract’s accounting assumes that received Ether can be freely managed, while in reality the balance becomes immutable. An attacker or any user who triggers the emergency withdrawal can cause Ether to be deposited into the treasury, after which the funds cannot be retrieved, effectively disappearing from the protocol’s usable pool. This situation manifests when the emergency withdrawal path is exercised; the treasury’s balance will increase, but the user interface will show no option to claim, withdraw, or exchange the funds, leading to symptoms such as “balance shows zero after expected refund” or “treasury holds ETH but I cannot move it”. The issue was discovered during a manual audit that inspected the treasury’s public interface and noticed the absence of any payable or withdraw functions. Because the contract compiles without errors and does not revert when receiving Ether, the problem can be subtle and may only be observed when a transaction actually sends Ether to the treasury. The impact is critical: funds become inaccessible, refunds may fail, and the protocol’s financial logic is broken, violating the assumption that all incoming assets are liquid. To remediate, the treasury should be extended with a function that either transfers the Ether to a designated address, swaps it for the funding token, or otherwise allocates it according to the protocol’s accounting rules, ensuring that deposited Ether can be reclaimed or utilized as intended.

## Recommendation
Add a function to convert the Ether to the fundingToken, or implement allocations to be able to use
the Ether.
