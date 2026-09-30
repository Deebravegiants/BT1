# [H] timestamp can overflow

## Summary
Severity: High
Reporter: Leo Alt, also found by Gyumin Roh
Contest weight: 0.3850
Dataset id: 4884
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Offline Memory argument in OpenVM relies on LogUp receives and sends of memory (any space) accesses, where each access has a monotonically increasing timestamp. Given two consecutive accesses (addr, time1) and (addr, time2), time2 > time1 is required and enforced by a constraint that time2 − time1 + 1 fits in 29 bits:  
The graph above shows a memory bus example where the origin and destination of an edge are a bus send and receive, respectively. Even though the difference between two timestamps is constrained, the timestamp itself is not, and can overflow the field's modulus.

Impact Explanation:  
If the timestamp overflows, an attacker can re-order the witness in an address space to execute wrong and malicious program paths. The graph below shows an example of an honest path in the overflow scenario:  
However, an attacker could re-order the bus interactions to the following graph:  
The bus interactions would be accepted by the verifier because all constraints are met, but note that the final memory values are simply wrong and the program results would be completely different from intended. A malicious prover could attempt to tweak the overflow to an advantageous program path. Note that the issue affects all address spaces.

## Proof of Concept
Each program instruction increases the timestamp by a certain amount, usually a small value like 3. More complex instructions can increase the timestamp by larger deltas, such as Keccak (46) and Bls12_381 (864). Designing such an exploit still requires considerable engineering work, so in the interest of time we describe a general strategy of:  
• Using 225 as the height for chips per segment.  
• Using complex circuits such as Keccak and Bls12_381 for many iterations.  
• Minimize memory accesses between iterations.  
• Perhaps a hand-written assembly program is required.

## Recommendation
timestamp could be range constrained to 30 bits.
