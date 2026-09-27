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
> The way to fix this is likely to adjust the commitment to be hiding the way that is done in the LegoSNARK paper (https://eprint.iacr.org/2019/142.pdf). To expand:
> 
> First, let me fix some notation.
> 
> Currently, the verifying key has two points on G2 used for checking the proof of knowledge for the commitment: `g` and `g'=-1/σ * g` (in the code: `VerifyingKey.CommitmentKey.G` and `VerifyingKey.CommitmentKey.GRootSigmaNeg`).
> The commitment itself is then `c = sum_i w_i * b_i`, where `b_i` are on G1, and the proof of knowledge associated to `c` is calculated as `pok = sum_i w_i * b'_i`, where `b'_i = σ*b_i` (in the code `b_i` and `b'_i` are `ProvingKey.CommitmentKeys.Basis[0][i]` and `ProvingKey.CommitmentKeys.BasisExpSigma[0][i]`). The proof of knowledge is then verified by checking `e(c, g) + e(pok, g') = 0` (I am using additive notation throughout here).
> 
> The Groth16 proof is verified by checking
> ```
> e(Krs, -[δ]₂) + e(c, -[γ]₂) + e(term involving public inputs, -[γ]₂) + other terms = 0
> ```
> 
> The construction ccGro16 from the LegoSNARK paper (page 73 in https://eprint.iacr.org/2019/142.pdf) is a similar construction. They do not have a proof of knowledge accompanying the commitment because they are considering the case where there are no public inputs. However, they claim that their scheme is zero-knowledge, and the crucial difference for this is that their commitment has an extra blinding term as is usual for Pedersen commitments. Concretely, it is of the form:
> ```
> c_new = sum_i w_i * b_i + v*[η/γ]₁
> ```
> where `[η/γ]₁` is a new element of G1 that is part of the proving key, with `η` a new toxic waste field element. The value of `v` is randomly chosen by the prover.
> 
> When adding this additional term to `c`, then to make the proof verification still succeeds, the proof point `Krs` is changed accordingly:
> ```
> Krs_new = Krs_old -  v*[η/δ]₁
> ```
> where `[η/δ]₁` is another new element of G1 that is part of the proving key. As `e([η/γ]₁, -[γ]₂) = e([η/δ]₁, -[δ]₂)`, the contributions from the new terms cancel each other in the proof verification pairing check.
> 
> This modification should ensure that the commitment is hiding.
> 
> The proof of knowledge would also need to be adapted accordingly, with
> ```
> pok = sum_i w_i * b'_i + v*[σ*η/γ]₁
> ```
> where `[σ*η/γ]₁` is another point of G1 to add to the proving key.
> 
> The above suggestion is meant as a starting point, I haven't fully thought through any additional interactions that there may be.

### Impact

The vulnerability affects only Groth16 proofs with commitments. Notably, PLONK proofs are not affected.

The vulnerability affects the zero-knowledge property of the proofs - in case the witness (secret or internal) values are small, then the attacker may be able to enumerate all possible choices to deduce the actual value. If the possible choices for the variables to be committed is large or there are many values committed, then it would be computationally infeasible to enumerate all valid choices.

It doesn't affect the completeness/soundness of the proofs.

### Patches

The vulnerability has been fixed in https://github.com/Consensys/gnark/pull/1245. Corresponding commit on the master branch https://github.com/Consensys/gnark/commit/afda68a38acca37becb8ba6d8982d03fee9559a0.

The patch to fix the issue is to add additional randomized value to the list of committed value at proving time to mask the rest of the values which were committed.

### Workarounds

The user can manually commit to a randomized value.
