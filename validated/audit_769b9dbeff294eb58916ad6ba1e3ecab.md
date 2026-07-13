Looking at the M-01 bug class — **accepting an object without verifying it was created by the authorized source** — I need to find a cb-mpc analog where an attacker-supplied object (key blob, access structure, public shares, partial decryption) is accepted without origin/binding verification, enabling a cryptographic attack.

Let me examine the most promising candidates I found: