# [M] Unconstrained Private Key Range in sssa.Create()

## Summary
Severity: Medium
Contest weight: 0.5929
Dataset id: 12188
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
HBTC Chain makes the unique innovation in creating, deploying, and managing secret shares among validators to enable cross-chain assets and their exchanges. The secret shares are developed based on the known Shamir secret sharing algorithm (sssa). The idea behind sssa is that it takes 푘+ 1 points to deﬁne a polynomial of degree 푘. For example, 2 points deﬁnes a line, 3 points deﬁnes a parabola, 4 points deﬁnes a cubic curve and so forth.
For a (푘, 푛) threshold scheme to share our secret 푆, the sssa algorithm typically chooses a random polynomial of degree 푘 1 with free term the secret. The polynomial does not take zero coeﬃcients. Also, the polynomial usually operates in a ﬁnite ﬁeld 퐹 of size 푃 where 0 < 푘 <= 푛 < 푃; 푆 < 푃 and 푃 is a large prime number.
```solidity
func keyGen(t int, coeff []big.Int, privateKeyShare ...btcec.PrivateKey) (btcec.PrivateKey, map[string]sssa.ShareXY, []btcec.PublicKey) {
    var newPriKey btcec.PrivateKey
    if len(privateKeyShare) > 0 {
        newPriKey = privateKeyShare[0]
    } else {
        newPriKey, _ = btcec.NewPrivateKey(btcec.S256())
    }
    share, cof := sssa.Create(t, n, newPriKey.D, coeff)
    return newPriKey, share, getCofCommits(cof)
}
```
푃 used for modulus operation, i.e., 푆 < 푃. If we follow the key generation execution path, we notice that a private key may be dynamically generated (in the above keyGen function at line 61) and directly passed to the sssa for secret share generation. Within the sssa algorithm, there is no check applied to ensure 푆 < 푃. The lack of 푆 < 푃 could potentially corrupt the generation of secret shares and may lead to unrecoverable loss of secret keys.
* Returns a new arary of secret shares (encoding x,y pairs as base64 strings) created by Shamir s Secret Sharing Algorithm requring a minimum number of share to recreate, of length shares, from the input secret raw as a string
```solidity
func Create(minimum int, shares int, priKey *big.Int, coeff []big.Int) (map[string]ShareXY, []big.Int) {
    // Verify minimum isnt greater than shares; there is no way to recreate the original polynomial in our current setup, therefore it doesn t make sense to generate fewer shares than are needed to reconstruct the secret.
    Convert the secret to its respective 256- bit big.Int representation
    // var secret []* big.Int = splitByteToInt ([] byte(raw))
    copy := big.NewInt(0).Set(priKey)
    copy = copy.Mod(copy, prime)
    secret := big.NewInt(0).Set(copy)
    // List of currently used numbers in the polynomial
    var numbers []big.Int = make([]big.Int, 0)
    numbers = append(numbers, big.NewInt(0))
    var coefficients []big.Int = make([]big.Int, 0)
    ...
}
```

## Recommendation
Apply the 푆 < 푃 check for proper generation of Shamir secret shares.
Public
