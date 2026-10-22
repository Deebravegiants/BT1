# [M] Proper Safe Prime Generation

## Summary
Severity: Medium
Contest weight: 0.4645
Dataset id: 12186
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon receiving a request for key generation, the settle daemon bootstraps the decentralized key-generation protocol [23] to generate secret key shares for participating parties (i.e., validators). Assume that the protocol runs among n parties: P1, ..., Pn, and the parties run on input threshold t and chosen elliptic curve parameters. It typically has the following three rounds:
Commitment Round:
Each party 푖 randomly generates a secret number 푢푖, and broadcasts a commit to the random point 푌푖 = 푢푖 퐺; Later on, each party broadcasts the corresponding decommitment to 푌푖, so that each party can independently verify the correctness for 푛 1 received decommitments. If there is any inconsistency, the protocol is aborted.
VSS Round:
Each party 푖 participates in the (푡, 푛) Feldman-VSS of the value 푢푖. The group public key is the resulting 푌 = Σ푗 푌푗 and the local secret share of party 푖 is 푥푖 = Σ푗 푓푗(푖). Each party 푗 randomly chooses the coeﬃcients for the polynomial function 푓푗(푥) and privately sends the calculated 푓푗(푖) result to party 푖. Note that the coeﬃcients essentially deﬁnes the polynomial and is the gist behind the Shamir secret-sharing algorithm (sssa). To properly notify other parties of its resulting secret share, the party 푖 broadcasts a zero-knowledge proof of 푥푖 (via Public discrete logarithms). Each party can independently verify other 푛 1 proofs and, if the proof fails, the protocol is aborted as well.
Paillier KeyGen Round:
Each party 푖 generates a Paillier keypair and broadcasts the public key 푒푖. Behind the scheme, each party generates its own safe primes 푝푖 and 푞푖 required by the Paillier keypair and broadcasts their zero-knowledge proofs of 푝푖, 푞푖 such that 푁푖 = 푝푖푞푖 (Note that 푁푖 is the RSA modulus associated with the Paillier encryption 푒푖). Similarly, each party independently veriﬁes 푛 1 received proofs and aborts otherwise.
It is important to note possible implications from square root attacks [24] that could aﬀect the Paillier KeyGen Round. Speciﬁcally, the best algorithms to compute discrete logarithms in arbitrary groups (of prime order) are the baby-step giant-step method, the rho method and the kangaroo method. These methods diﬀer in their complexity and memory-space tradeoﬀs. To avoid these attacks, a best practice is to ensure the prime numbers 푝푖, 푞푖 behind the RSA modulus 푁 have suﬃciently large diﬀerence (typically 1024 bits).
However, it appears that the prime numbers generated in RSAParameter() do not follow the above best practice. Notice that it does have certain checks in place to ensure the generated PTilde and QTilde are not identical (line 30 in the code snippet below). However, it is also equally important to ensure their diﬀerence is suﬃciently large to avoid the above mentioned square-root attacks.
```solidity
func RSAParameter(bits int) (big.Int, big.Int, big.Int, big.Int, big.Int, error) {
    //gP (PTilde -1)=gP 2p=1 mod PTilde
    PTilde, gP, err1 := safePrimeAndGenerator(bits)
    for err1 != nil {
        fmt.Println("SafePrimeAndGenerator 1 fail!")
        PTilde, gP, err1 = safePrimeAndGenerator(bits)
    }
    //gQ (QTilde -1)=gQ 2q=1 mod QTilde
    QTilde, gQ, err2 := safePrimeAndGenerator(bits)
    for err2 != nil {
        fmt.Println("SafePrimeAndGenerator 2 fail!")
        QTilde, gQ, err2 = safePrimeAndGenerator(bits)
    }
    // Chinese Remainder Theorem requires gcd(m1,m2)=1
    for PTilde.Cmp(QTilde) == 0 {
        fmt.Println("Same safe prime!")
        PTilde, gP, err1 = safePrimeAndGenerator(bits)
        for err1 != nil {
            fmt.Println("SafePrimeAndGenerator 1 fail!")
            PTilde, gP, err1 = safePrimeAndGenerator(bits)
        }
        QTilde, gQ, err2 = safePrimeAndGenerator(bits)
        for err2 != nil {
            fmt.Println("SafePrimeAndGenerator 2 fail!")
            QTilde, gQ, err2 = safePrimeAndGenerator(bits)
        }
    }
    p := big.NewInt(0).Rsh(big.NewInt(0).Sub(PTilde, one), 1)
    q := big.NewInt(0).Rsh(big.NewInt(0).Sub(QTilde, one), 1)
    NTilde := big.NewInt(0).Mul(PTilde, QTilde)
    t1 := big.NewInt(0).ModInverse(QTilde, PTilde)
    t2 := big.NewInt(0).ModInverse(PTilde, QTilde)
    b01 := big.NewInt(0).Mul(big.NewInt(0).Mul(gP, t1), QTilde)
    b02 := big.NewInt(0).Mul(big.NewInt(0).Mul(gQ, t2), PTilde)
    b0 := big.NewInt(0).Mod(big.NewInt(0).Add(b01, b02), NTilde)
    ...
    return NTilde, PTilde, QTilde, h1, h2, nil
}
```

## Recommendation
It is strongly recommended to ensure that safe primes generated are of the desired quality and length. In particular, when generating two RSA safe primes 푝푖 and 푞푖 for Paillier encryption with 푁 = 푝푖푞푖, there is a need to ensure that the diﬀerence 푝푖 푞푖 is also very large (say 1020 bits) in order to avoid square-root attacks.
