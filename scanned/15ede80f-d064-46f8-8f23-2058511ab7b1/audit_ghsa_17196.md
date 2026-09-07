# [H] Go SDK for CloudEvents's use of WithRoundTripper to create a Client leaks credentials

## Summary
Severity: High
Advisory: GHSA-5pf6-2qwx-pxm2
CVE: CVE-2024-28110
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-5pf6-2qwx-pxm2
Type: github-advisory

## Affected
- Go: `github.com/cloudevents/sdk-go/v2` — affected >=0 <2.15.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
Using cloudevents.WithRoundTripper to create a cloudevents.Client with an authenticated http.RoundTripper causes the go-sdk to leak credentials to arbitrary endpoints.

The relevant code is [here](https://github.com/cloudevents/sdk-go/blob/67e389964131d55d65cd14b4eb32d57a47312695/v2/protocol/http/protocol.go#L104-L110) (also inline, emphasis added):

<pre>if p.Client == nil {
  p.Client = **http.DefaultClient**
}

if p.roundTripper != nil {
  p.Client.**Transport = p.roundTripper**
}
</pre>

When the transport is populated with an authenticated transport such as:
- [oauth2.Transport](https://pkg.go.dev/golang.org/x/oauth2#Transport)
- [idtoken.NewClient(...).Transport](https://pkg.go.dev/google.golang.org/api/idtoken#NewClient)

... then http.DefaultClient is modified with the authenticated transport and will start to send Authorization tokens to
**any endpoint** it is used to contact!

Found and patched by: @tcnghia and @mattmoor

### Patches
v.2.15.2

## References
- https://github.com/cloudevents/sdk-go/security/advisories/GHSA-5pf6-2qwx-pxm2
- https://github.com/cloudevents/sdk-go/commit/de2f28370b0d2a0f64f92c0c6139fa4b8a7c3851
- https://github.com/cloudevents/sdk-go
- https://github.com/cloudevents/sdk-go/blob/67e389964131d55d65cd14b4eb32d57a47312695/v2/protocol/http/protocol.go#L104-L110
