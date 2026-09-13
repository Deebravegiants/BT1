# [H] Missing Tests for Edge Cases

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
There are no test cases for invalid proof and public input such as proof elements not on curve, proof element is points of infinity, all proof elements are zero, wrong proof element, proof scalar element bigger than scalar field modulus, proof scalar element wrapping around scalar field modulus, public input greater than scalar field modulus etc. and no or multiple BSB22 commitments. There is only test for valid proof and one BSB22 commitment. Tests for all edge cases are crucial to check proof soundness in SNARK, missing it may result in missing some critical bugs, e.g. issue 15 


#### Recommendation
Add missing test cases 
<!-- Supply advice on how to best fix the problem. -->
