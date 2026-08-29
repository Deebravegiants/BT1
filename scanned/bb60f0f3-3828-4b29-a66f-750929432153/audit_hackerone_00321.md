# [H] CryptoNote: remote node DoS

## Summary
Severity: High (CVSS 7.5)
Program: Monero
Weakness: Uncontrolled Resource Consumption
Reporter: anonimal
State: resolved
Disclosed: 2019-07-03T00:20:02.687Z
Source: https://hackerone.com/reports/506595

## Details
## Summary:

Remote node DoS. See patch below.

## Releases Affected:

All Monero versions, including the recent v0.14.0.2. Possibly all CryptoNote implementations that aren't Zano.

## Steps To Reproduce:

Since this is *currently* a theoretical attack, non-code PoC detailed in the patch below.

## Supporting Material/References:

Based against current `master` `49afbd0c53d29656689f319c7d3543204ead4e59`:

```diff
commit 6620d099800d8935596f59834ce389868b2851f0 (HEAD -> cryptonote)
gpg: Signature made Fri 08 Mar 2019 02:57:58 AM UTC
gpg:                using RSA key 12186272CD48E2539E2DD29B66A76ECF914409F1
gpg: using pgp trust model
gpg: Good signature from "anonimal <anonimal@getmonero.org>" [ultimate]
gpg:                 aka "anonimal <anonimal@kovri.io>" [ultimate]
gpg:                 aka "anonimal <anonimal@sekreta.org>" [ultimate]
gpg: binary signature, digest algorithm SHA256, key algorithm rsa4096
Author: anonimal <anonimal@getmonero.org>
Date:   Fri Mar 8 02:21:38 2019 +0000

    cryptonote_protocol_handler: prevent potential DoS
    
    Essentially, one can send such a large amount of IDs that core exhausts
    all free memory. This issue can theoretically be exploited using very
    large CN blockchains, such as Monero.
    
    Credit given to CryptoNote author 'cryptozoidberg' for the fix.

diff --git a/src/cryptonote_protocol/cryptonote_protocol_handler.h b/src/cryptonote_protocol/cryptonote_protocol_handler.h
index efd986b53..c9e35d2d9 100644
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/506595_
