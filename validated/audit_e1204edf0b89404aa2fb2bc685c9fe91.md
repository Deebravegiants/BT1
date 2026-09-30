The user is asking to find an analog in the `Alyssadaypin/rsk-powhsm--019` codebase to a vulnerability where a single manager can bypass a review threshold by repeatedly calling a function. The core of the vulnerability is the lack of a check to ensure a manager has not already voted, allowing them to increment a counter multiple times to reach a threshold.

In the `Alyssadaypin/rsk-powhsm--019` codebase, the `do_authorize_signer` function in `firmware/src/ledger/ui/src/signer_authorization.c` handles the authorization of new signer versions. This process involves collecting signatures from multiple authorized parties to reach a `THRESHOLD_AUTHORIZERS` value. The vulnerability analog would be if a single authorized signer could submit multiple signatures, thereby bypassing the multi-signature threshold.

### Title
Single Authorized Signer Can Bypass Multi-Signature Threshold - ()

### Summary
A single authorized signer can bypass the multi-signature threshold for authorizing a new signer version by submitting multiple signatures, as there is no mechanism to track which authorizers have already provided a valid signature. This allows one authorized party to unilaterally approve a new signer version.

### Finding Description
The `do_authorize_signer` function, specifically within the `OP_SIGAUT_SIGN` case, iterates through `TOTAL_AUTHORIZERS` to verify signatures against `authorizers_pubkeys` . If a signature is valid, the corresponding `authorized_signer_verified[i]` flag is set to `true` . The `valid_count` is then incremented for each `true` flag . However, there is no check to prevent the same authorized signer from submitting multiple valid signatures for the same `auth_hash` . This means a single authorized signer could call `OP_SIGAUT_SIGN` multiple times with their signature, incrementing `valid_count` each time until `valid_count >= THRESHOLD_AUTHORIZERS` is met .

### Impact Explanation
This vulnerability allows a single authorized signer to unilaterally authorize a new signer version, bypassing the intended multi-signature security mechanism. This could lead to an unauthorized or malicious signer version being installed on the device, potentially compromising the security of the HSM and the funds it protects.

### Likelihood Explanation
The likelihood is high because the mechanism to prevent a single authorized signer from repeatedly submitting their signature is absent. An attacker with access to one authorized key could exploit this by simply sending multiple `OP_SIGAUT_SIGN` commands.

### Recommendation
Implement a mechanism to track which authorized signers have already submitted a valid signature for the current `auth_hash`. This could involve storing a bitmap or an array of booleans, indexed by the authorizer's position, and checking it before incrementing `valid_count`.

### Proof of Concept
An unprivileged party, specifically a holder of one of the `AUTHORIZERS_PUBKEYS` , can perform the following sequence of APDU commands:

1.  **`OP_SIGAUT_SIGVER`**: Send the new signer hash and iteration to the device. The device will compute the `auth_hash` to be signed .
2.  **`OP_SIGAUT_SIGN` (repeatedly)**: The authorized signer then signs the `auth_hash` with their private key. They can send this signature `THRESHOLD_AUTHORIZERS` times. Each time, the `do_authorize_signer` function will verify the signature  and increment `valid_count` . Since `authorized_signer_verified[i]` is a boolean flag that is set to true if a valid signature is found for that authorizer , and there's no check to see if the *same* authorizer has already contributed to the `valid_count` for the current authorization attempt, the `valid_count` will increase with each submission of the same valid signature.
3.  Once `valid_count` reaches `THRESHOLD_AUTHORIZERS` , the new signer version will be written to NVM , effectively authorizing it.

## Notes
The `signer_authorization` module is designed to ensure that firmware upgrades are approved by a multi-signature threshold of administrative public keys . The `THRESHOLD_AUTHORIZERS` is defined as `TOTAL_AUTHORIZERS / 2 + 1` , indicating an intent for a majority consensus. The current implementation, however, only checks if a signature is valid and increments a counter, without tracking unique contributions per authorization attempt.

Wiki pages you might want to explore:
- [Signer Authorization and Upgrades (Alyssadaypin/rsk-powhsm--019)](/wiki/Alyssadaypin/rsk-powhsm--019#4.2)

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_2f222a86-98e2-43d7-9a8a-6f7e28c583a3
