# [M] Denial of service of Minder Server from maliciously crafted GitHub attestations

## Summary
Severity: Medium
Advisory: GHSA-8fmj-33gw-g7pw
CVE: CVE-2024-35238
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-8fmj-33gw-g7pw
Type: github-advisory

## Affected
- Go: `github.com/stacklok/minder` — affected >=0 <0.0.51

## Details
Minder is vulnerable to a denial-of-service (DoS) attack which could allow an attacker to crash the Minder server and deny other users access to it.

The root cause of the vulnerability is that Minders sigstore verifier reads an untrusted response entirely into memory without enforcing a limit on the response body. An attacker can exploit this by making Minder make a request to an attacker-controlled endpoint which returns a response with a large body which will crash the Minder server.

Specifically, the point of failure is where Minder parses the response from the GitHub attestations endpoint in `getAttestationReply`. Here, Minder makes a request to the `orgs/$owner/attestations/$checksumref` GitHub endpoint (line 285) and then parses the response into the `AttestationReply` (line 295):

https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/verifier/sigstore/container/container.go#L271-L300

The way Minder parses the response on line 295 makes it prone to DoS if the response is large enough. Essentially, the response needs to be larger than the machine has available memory.

To demonstrate this in an isolated way, consider the following example:

```go
package main

import (
        "encoding/json"
        "fmt"
        "io"
        "strings"
)

type Attestation struct {
        Bundle json.RawMessage `json:"bundle"`
}

type AttestationReply struct {
        Attestations []Attestation `json:"attestations"`
}

func main() {
        m1 := strings.NewReader("{\"attestations\":[")
        maliciousBody := strings.NewReader(strings.Repeat("{\"bundle\":{\"k\": \"v\"{{,", 100000000))
        m2 := strings.NewReader("{\"bundle\":{\"k\": \"v\"}}]}")
        maliciousBodyReader := io.MultiReader(m1, maliciousBody, maliciousBody, maliciousBody, m2)
        fmt.Println("Created malicious body")

        var attestationReply AttestationReply
        _ = json.NewDecoder(maliciousBodyReader).Decode(&attestationReply)
}

```

This example mimics the behavior of Minders `getAttestationReply` and how a malicious response body passed to `getAttestationReply’s` parsing of the response will cause DoS.

When running this script locally on my system, Go incrementally increases memory consumption up to above 90%, freezes the machine and then performs a sigkill.

## Attack vector
The content that is hosted at the `orgs/$owner/attestations/$checksumref` GitHub attestation endpoint is controlled by users including unauthenticated users to Minders threat model. However, a user will need to configure their own Minder settings to cause Minder to make Minder send a request to fetch the attestations. The user would need to know of a package whose attestations were configured in such a way that they would return a large response when fetching them. As such, the steps needed to carry out this attack would look as such:

1. The attacker adds a package to ghcr.io with attestations that can be fetched via the `orgs/$owner/attestations/$checksumref` GitHub endpoint.
2. The attacker registers on Minder and makes Minder fetch the attestations.
3. Minder fetches attestations and crashes thereby being denied of service.

## References
- https://github.com/stacklok/minder/security/advisories/GHSA-8fmj-33gw-g7pw
- https://nvd.nist.gov/vuln/detail/CVE-2024-35238
- https://github.com/stacklok/minder/commit/fe321d345b4f738de6a06b13207addc72b59f892
- https://github.com/stacklok/minder
- https://github.com/stacklok/minder/blob/daccbc12e364e2d407d56b87a13f7bb24cbdb074/internal/verifier/sigstore/container/container.go#L271-L300
