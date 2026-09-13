# [M] kuma-dp connects to control plane without verifying TLS certificate when no CA is configured

## Summary
Severity: Medium
Advisory: GHSA-wvmp-6r4v-j6cv
CVE: CVE-2026-52724
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:4.0/AV:A/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-wvmp-6r4v-j6cv
Type: github-advisory

## Affected
- Go: `github.com/kumahq/kuma/v2` — affected >=0 <2.7.26
- Go: `github.com/kumahq/kuma/v2` — affected >=2.8.0 <2.9.16
- Go: `github.com/kumahq/kuma/v2` — affected >=2.10.0 <2.11.14
- Go: `github.com/kumahq/kuma/v2` — affected >=2.12.0 <2.12.11
- Go: `github.com/kumahq/kuma/v2` — affected >=2.13.0 <2.13.7
- Go: `github.com/kumahq/kuma` — affected >=0

## Details
When kuma-dp is started against an HTTPS control plane and the operator did not pass a CA certificate, the data plane connects with TLS peer verification disabled. The dataplane authentication token is sent over this unverified connection

## Impact

An on-path attacker can intercept the dataplane authentication token and impersonate the control plane to the data plane, allowing them to inject a forged bootstrap configuration and take over the proxy

## Affected configurations

- Universal mode `kuma-dp` started against an HTTPS control plane without `--ca-cert-file` (or `KUMA_CONTROL_PLANE_CA_CERT` unset)

## Not affected

- Kubernetes installs done through the standard installers (`kumactl install control-plane` or the official Helm chart). In both cases the control plane's mutating admission webhook injects `KUMA_CONTROL_PLANE_CA_CERT` into every sidecar at pod admission, so each `kuma-dp` starts with the CA already configured

## Workarounds

Set `--ca-cert-file` (or `KUMA_CONTROL_PLANE_CA_CERT`) on every Universal mode data plane and point it at the control plane's serving CA. Alternatively, terminate the control plane behind a publicly trusted certificate; the patched releases will verify successfully against the operating system trust store with no further configuration

## Resources

- Fix: https://github.com/kumahq/kuma/pull/16777

## References
- https://github.com/kumahq/kuma/security/advisories/GHSA-wvmp-6r4v-j6cv
- https://github.com/kumahq/kuma/pull/16777
- https://github.com/kumahq/kuma/commit/2ecadac1aa2fd8cded4c2ab768949f4c2ec83e2a
- https://github.com/kumahq/kuma
