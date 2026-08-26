# [M] Commitments to private witnesses in Groth16 as implemented break zero-knowledge property

## Summary
Severity: Medium
Chain: ZK
Component: Consensys/gnark
CVE: CVE-2024-45040
Published: 2024-09-06
Source: https://github.com/Consensys/gnark/security/advisories/GHSA-9xcg-3q8v-7fq6
Type: github-advisory

## Details
Reported by @maltezellic. Thanks for reporting the issue!

From the correspondence:
> This report concerns the Groth16 prover when used with commitments (as in `frontend.Committer`). To simplify exposition of the issue, I will focus on the case of a single commitment, to only private witnesses. But the issue should be present whenever commitments are used that include private witnesses.
>
> The commitment to private witnesses `w_i` is computed as
> ```
> c = sum_i w_i * b_i
> ```
> where `b_i` would be `ProvingKey.CommitmentKeys[0].Basis[i]` in the code.
> 
> While this is a binding commitment, it is not hiding. In practice, an adversary will know the points `b_i`, as they are part of the proving key, and can verify correctness of a guess for the values of `w_i` by computing `c'` as the right hand side of the above formula, and checking whether `c'` is equal to `c`. I attach a proof of concept that demonstrates this.
> 
> This breaks the perfect zero-knowledge property of Groth16, so the Groth16 scheme using commitments to private witnesses as implemented by gnark fails to be a zk-SNARK.
> 
> The code indicates that the extension to Groth16 given by the commitments follows the paper "Recursion over Public-Coin Interactive Proof Systems; Faster Hash Verification" by Alexandre Belling, Azam Soleimanian, and Olivier Begassat. In that paper, it seems that commitments are applied to what were originally public inputs, which are moved to private witnesses for efficiency reasons. In any case, that paper does not discuss any hiding/privacy/zero-knowledge properties of their protocols.
> 
> So for the use-cases envisioned by that paper, having the commitment not be hiding and losing zero-knowledge of Groth16 might be adequate. However, the documentation by gnark does not make clear that committing to private witnesses loses the zero-knowledge property. The documentation for `frontend.Committer` does not mention this, and the following snippet from `std/multicommit/doc_test.go`, where private witness variables are named `Secrets` and are committed, seems to actively suggest that committed witnesses are still private.
> ```go
> // MultipleCommitmentCircuit is an example circuit showing usage of multiple
> // independent commitments in-circuit.
> type MultipleCommitmentsCircuit struct {
>     Secrets [4]frontend.Variable
> }
> 
> func (c *MultipleCommitmentsCircuit) Define(api frontend.API) error {
>     // first callback receives first unique commitment derived from the root commitment
>     multicommit.WithCommitment(api, func(api frontend.API, commitment frontend.Variable) error {
>         // compute (X-s[0]) * (X-s[1]) for a random X
>         res := api.Mul(api.Sub(commitment, c.Secrets[0]), api.Sub(commitment, c.Secrets[1]))
>         api.AssertIsDifferent(res, 0)
>         return nil
>     }, c.Secrets[:2]...)
>    // ...
> ```
> 
> Thus it seems to me that the intention likely was (and users will be expecting) that gnark's implementation of Groth16 with these commitments should still have zero-knowledge and that the commitments should be hiding.
> 

_Trimmed to 38 lines — full report: https://github.com/Consensys/gnark/security/advisories/GHSA-9xcg-3q8v-7fq6_
