# Q0720: Custody package encrypted to an attacker-supplied key in Package (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker supply the self-custody public key/identity material through their scanned payload so `Package` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) encrypts or addresses the biometric custody package to a key of the attacker's choosing rather than one bound to the verified user?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `Package` (type)
- Entrypoint: Identity/key material carried in the scanned QR payload
- Attacker controls: the public key bytes and identity fields in the payload
- Exploit idea: Trace the key used by `Package` back to its origin and check for authenticity binding before use.
- Invariant to test: Custody material is encrypted only to a key whose binding to the enrolling user is verified.
- Expected Immunefi impact: Another person's biometric package recoverable by the attacker
- Fast validation: Integration test substituting an attacker key and asserting the package build is refused.
