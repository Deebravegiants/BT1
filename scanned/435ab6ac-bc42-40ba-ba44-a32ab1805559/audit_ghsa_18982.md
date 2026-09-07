# [H] Evervault Go SDK: Incomplete PCR Validation in Enclave Attestation for non-Evervault hosted Enclaves

## Summary
Severity: High
Advisory: GHSA-88h9-77c7-p6w4
CVE: CVE-2025-64186
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-11-12
Source: https://github.com/advisories/GHSA-88h9-77c7-p6w4
Type: github-advisory

## Affected
- Go: `github.com/evervault/evervault-go` — affected >=0 <1.3.2

## Details
### Summary

A vulnerability was identified in the `evervault-go` SDK’s attestation verification logic that may allow incomplete documents to pass validation. This may cause the client to trust an enclave operator that does not meet expected integrity guarantees.

The exploitability of this issue is limited in Evervault-hosted environments as an attacker would require the pre-requisite ability to serve requests from specific evervault domain names, following from our ACME challenge based TLS certificate acquisition pipeline. 

The vulnerability primarily affects applications which only check PCR8. Though the efficacy is also reduced for applications that check all PCR values, the impact is largely remediated by checking PCR 0, 1 and 2.
 

### Patches
The identified issue has been addressed in version [1.3.2](https://github.com/evervault/evervault-go/pull/48) by validating attestation documents before storing in the cache, and replacing the naive equality checks with a new SatisfiedBy check.

### Workarounds
If you are using evervault-go to attest Enclaves that are hosted outside of Evervault environments and cannot upgrade:

1) Modify your application logic to fail verification if PCR8 is not explicitly present and non-empty
2) Add custom pre-validation to reject documents that omit any required PCRs.

### POC
```
package evervault
import (
        "testing"

        "github.com/evervault/evervault-go/attestation"
        "github.com/stretchr/testify/assert"
        "github.com/hf/nitrite"
)


func TestVulnerableCompare(t *testing.T) {
          assert := assert.New(t)
          // arrange
          expectedPCRs := []attestation.PCRs{
                attestation.PCRs{
                      PCR0:
"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001",
                      PCR1:
"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002",
                      PCR2:
"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003",
                      PCR8:
"000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004",
                     },
           }
            actualDocument := nitrite.Document {}
            actualDocument.PCRs = map[uint][]byte{
                    10: make([]byte, 32),
            }
            // act
            v := verifyPCRs(expectedPCRs, actualDocument)
            
            // assert
            // Verify should not pass but it does
            
            assert.Equal(true, v)
}
```

## References
- https://github.com/evervault/evervault-go/security/advisories/GHSA-88h9-77c7-p6w4
- https://nvd.nist.gov/vuln/detail/CVE-2025-64186
- https://github.com/evervault/evervault-go/pull/48
- https://github.com/evervault/evervault-go/commit/7c824d289bba11ec0bea46a338023f5b128bbb28
- https://github.com/evervault/evervault-go
