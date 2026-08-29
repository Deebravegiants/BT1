# [M]  `check_reserve_proof` sums RingCT ECDH amounts without checking the output commitment

## Summary
Severity: Medium (CVSS 4.7)
Program: Monero
Weakness: Missing Required Cryptographic Step
Reporter: bebensap
State: resolved
Disclosed: 2026-08-05T10:23:44.117Z
Source: https://hackerone.com/reports/3698862

## Details
**Repository:** [`monero-project/monero`](https://github.com/monero-project/monero) — `src/wallet/wallet2.cpp`, `src/ringct/rctSigs.cpp`. Snapshot: `master @ 3ad4a5ee8` (`v0.18.1.0-3ad4a5ee8`).

## Summary

`wallet2::check_reserve_proof` proves that a reserve-proof entry belongs to the claimed wallet, then decodes the RingCT amount from `tx.rct_signatures.ecdhInfo[proof.index_in_tx]` and adds it to `total`. The missing step is the one normal wallet decoding already does: recompute the Pedersen commitment from the decoded `(mask, amount)` and compare it to `tx.rct_signatures.outPk[n].mask`.

The vulnerable block is in `wallet2.cpp` around 12751–12764:

```cpp
uint64_t amount = tx.vout[proof.index_in_tx].amount;
if (amount == 0)
{
  crypto::secret_key shared_secret;
  crypto::derivation_to_scalar(derivation, proof.index_in_tx, shared_secret);
  rct::ecdhTuple ecdh_info = tx.rct_signatures.ecdhInfo[proof.index_in_tx];
  rct::ecdhDecode(ecdh_info, rct::sk2rct(shared_secret),
      tx.rct_signatures.type == rct::RCTTypeBulletproof2 ||
      tx.rct_signatures.type == rct::RCTTypeCLSAG ||
      tx.rct_signatures.type == rct::RCTTypeBulletproofPlus);
  amount = rct::h2d(ecdh_info.amount);   // no C == mask*G + amount*H check
}
total += amount;
```

For comparison, the wallet receive path does not trust that decoded value by itself:

```cpp
const rct::key C = tx.rct_signatures.outPk[n].mask;
rct::key Ctmp;
rct::addKeys2(Ctmp, ecdh_info.mask, ecdh_info.amount, rct::H);
if (rct::equalKeys(C, Ctmp))
  amount = rct::h2d(ecdh_info.amount);
else
  amount = 0;
```

The lower-level RingCT helper is stricter too. `decodeRctSimple()` throws `warning, amount decoded incorrectly, will be unable to spend` when the decoded ECDH tuple does not match the output commitment.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3698862_
