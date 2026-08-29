# [M] Groth16 commitment extension unsound for more than one commitment

## Summary
Severity: Medium
Chain: ZK
Component: Consensys/gnark
CVE: CVE-2024-45039
Published: 2024-09-06
Source: https://github.com/Consensys/gnark/security/advisories/GHSA-q3hw-3gm4-w5cr
Type: github-advisory

## Details
### Description

Thanks @maltezellic for reporting the issue.

From the correspondence:

> I believe I found another vulnerability in gnark's Groth16 backend's commitments extension, this one impacts soundness whenever more than one commitment is used, making it more critical than the previous issue.
> 
> The summary is that the proof of knowledge associated to a commitment is crucial to bind the commitment to the actual circuit variables that were supposed to be committed. However, the same σ is used for all proofs of knowledge for the commitments, which allows mixing between them, making it possible to fix the value of all but one commitment before choosing the circuit variable assignments.
> 
> In more detail:
> To simplify notation, let us consider the case of two commitments, each to only a single variable. Let's say the basis elements for those commitments are `K_0` and `K_1`. Then the proving key will contain `K_0` and `K_1`, and also `σ*K_0` and `σ*K_1` for the proof of knowledge. The honest prover assigning a to the first circuit variable and b to the second will then produce commitments
> `D_0 = a*K_0`
> `D_1 = b*K_1`
> Out of the two D's, a challenge r for the commitment folding will be generated. The folded commitment will then be
> `D_folded = D_0 + r*D_1 = a*K_0 + r*b*K_1`
> The honest prover will supply a fitting proof of knowledge
> `P = a*(σ*K_0) + r*b*(σ*K_1)`
> 
> Now the verifier will only use all of this in two ways:
> 1. In the check of the Groth16 proof itself, where only the sum `D_0 + D_1` is used.
> 2. In the proof of knowledge check, where it will be verified that P is indeed `σ*(D_0 + r*D_1)`, with r calculated from `D_0` and `D_1` as before.
> 
> This has the following implications. In the following, a malicious prover's points will have an apostrophe appended, and we keep `D_0` etc. for the legitimate values:
> 1. A malicious prover is only forced to provide `D'_0` and `D'_1` such that the sum is correct. So they can use arbitrary `D'_0` as long as they set `D'_1 = D_0 + D_1 - D'_0`.
> 2. After choosing `D'_0` and `D'_1`, the prover can always calculate r. Evaluating `σ*(D'_0 + r*D'_1)` is then possible as long as both `D'_0` and `D'_1` are linear combinations of basis elements for which σ times that basis element is known. In particular, this works as long as `D'_0` and `D'_1` are linear combinations of `K_0` and `K_1`.
> 
> The upshot is that a malicious prover can choose arbitrary a' and b', and then set
> `D'_0 = a'*K_0 + b'*K_1`
> `D'_1 = (a - a')*K_0 + (b - b')*K_1`
> Then they calculate r for this, and set
> `P = (a' + r*(a-a'))*(σ*K_0) + (b' + r*(b-b'))*(σ*K_1)`
> This will then be accepted as a valid proof. Yet the first commitment point can be chosen completely independently of a and b, so in particular the malicious prover can use a constant for this, so that they will know the in-circuit challenge that will be added to the public inputs before they have to choose the witness assignments. For most use cases of such challenges (for proving things with Fiat-Shamir, random linear combinations etc.) this causes a critical soundness problem.
> 
> The problem generalizes to more than two commitments and commitments to more than one circuit variable each; one can freely choose all but one commitment as arbitrary linear combinations of the basis elements for all commitments, and then must choose the one remaining commitment in such a way that the sum is correct.
> 
> The root cause of the issue is that the σ used for the proofs of knowledge is the same, allowing to mix between the basis elements, as one has σ times them available for all of them.
> So the fix is to have a separate σ for each commitment. So in our example above, the proving key would have the basis elements `K_0` and `K_1`, and for the proofs of knowledge now `σ_0*K_0` and `σ_1*K_1`. Folding the commitments would not be possible in the same way now, so the verifier will have to do more pairings. The prover could still provide a folded proof of knowledge however. With

_Trimmed to 38 lines — full report: https://github.com/Consensys/gnark/security/advisories/GHSA-q3hw-3gm4-w5cr_
