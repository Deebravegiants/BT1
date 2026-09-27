# [H] Distribution affected by pull-through cache credential exfiltration via www-authenticate bearer realm

## Summary
Severity: High
Advisory: GHSA-3p65-76g6-3w7r
CVE: CVE-2026-33540
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-3p65-76g6-3w7r
Type: github-advisory

## Affected
- Go: `github.com/distribution/distribution/v3` — affected >=0 <3.1.0
- Go: `github.com/distribution/distribution` — affected >=0

## Details
hi guys,

commit: 40594bd98e6d6ed993b5c6021c93fdf96d2e5851 (as-of 2026-01-31)
contact: GitHub Security Advisory (https://github.com/distribution/distribution/security/advisories/new)

## summary

in pull-through cache mode, distribution discovers token auth endpoints by parsing `WWW-Authenticate` challenges returned by the configured upstream registry. the `realm` URL from a bearer challenge is used without validating that it matches the upstream registry host. as a result, an attacker-controlled upstream (or an attacker with MitM position to the upstream) can cause distribution to send the configured upstream credentials via basic auth to an attacker-controlled `realm` URL.

this is the same vulnerability class as CVE-2020-15157 (containerd), but in distribution’s pull-through cache proxy auth flow.

## severity

HIGH

note: the baseline impact is credential disclosure of the configured upstream credentials. if a deployment uses broader credentials for upstream auth (for example cloud iam credentials), the downstream impact can be higher; i am not claiming this as default for all deployments.

## impact

credential exfiltration of the upstream authentication material configured for the pull-through cache.

attacker starting positions that make this realistic:
- supply chain / configuration: an operator configures a proxy cache to use an upstream that becomes attacker-controlled (compromised registry, stale domain, or a malicious mirror)
- network: MitM on the upstream connection in environments where the upstream is reachable over insecure transport or a compromised network path

## affected components

- `registry/proxy/proxyauth.go:66-81` (`getAuthURLs`): extracts bearer `realm` from upstream `WWW-Authenticate` without validating destination
- `internal/client/auth/session.go:485-510` (`fetchToken`): uses the realm URL directly for token fetch
- `internal/client/auth/session.go:429-434` (`fetchTokenWithBasicAuth`): sends credentials via basic auth to the realm URL

## reproduction

attachment: `poc.zip` (local harness) with canonical and control runs.

the harness is local and does not contact a real registry: it uses two local HTTP servers (upstream + attacker token service) to demonstrate whether basic auth is sent to an attacker-chosen realm.

```bash
unzip -q -o poc.zip -d poc
cd poc
make canonical
make control
```

expected output (excerpt):

```
[CALLSITE_HIT]: getAuthURLs::configureAuth
[PROOF_MARKER]: basic_auth_sent=true realm_host=127.0.0.1 account_param=user authorization_prefix=Basic
```

control output (excerpt):

```
[CALLSITE_HIT]: getAuthURLs::configureAuth
[NC_MARKER]: realm_validation=PASS basic_auth_sent=false
```

## suggested remediation

validate that the token `realm` destination is within the intended trust boundary before associating credentials with it or sending any authentication to it. one conservative option is strict same-host binding: only accept a realm whose host matches the configured upstream host.

## fix accepted when

- distribution does not send configured upstream credentials to an attacker-chosen realm URL
- a regression test covers the canonical and blocked cases

[addendum.md](https://github.com/user-attachments/files/24984637/addendum.md)
[poc.zip](https://github.com/user-attachments/files/24984638/poc.zip)
[PR_DESCRIPTION.md](https://github.com/user-attachments/files/24984639/PR_DESCRIPTION.md)
[RUNNABLE_POC.md](https://github.com/user-attachments/files/24984640/RUNNABLE_POC.md)


best,
oleh

## References
- https://github.com/distribution/distribution/security/advisories/GHSA-3p65-76g6-3w7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-33540
- https://github.com/distribution/distribution/commit/cc5d5fa4ba02157501e6afa2cc6a903ad0338e7b
- https://github.com/distribution/distribution
