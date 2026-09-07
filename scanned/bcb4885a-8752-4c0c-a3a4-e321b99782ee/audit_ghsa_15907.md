# [H] Pomerium service account access token may grant unintended access to databroker API

## Summary
Severity: High
Advisory: GHSA-r7rh-jww5-5fjr
CVE: CVE-2024-47616
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-r7rh-jww5-5fjr
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.27.1

## Details
### Impact

We've identified a vulnerability in the Pomerium databroker service API that may grant unintended access under specific conditions. This affects only certain Pomerium Zero and Pomerium Enterprise deployments.

#### Who is affected?

A Pomerium deployment is susceptible to this issue if _all_ of the following conditions are met:
- You have issued a [service account](https://www.pomerium.com/docs/capabilities/service-accounts) access token using Pomerium Zero or Pomerium Enterprise.
- The access token has an explicit expiration date in the future.
- The core Pomerium databroker gRPC API is not otherwise secured by network access controls.

If your deployment does not meet _all_ of these conditions, you are not affected by this vulnerability.

#### Details

The Pomerium databroker service is responsible for managing all persistent Pomerium application state. Requests to the databroker service API are authorized by the presence of a JSON Web Token (JWT) signed by a key known by all Pomerium services in the same deployment. However, incomplete validation of this JWT meant that some service account access tokens would incorrectly be treated as valid for the purpose of databroker API authorization.

Improper access to the databroker API could allow exfiltration of user info, spoofing of user sessions, or tampering with Pomerium routes, policies, and other settings.

#### Discovery

This issue was discovered during internal review. At this time we have no evidence to suggest that this vulnerability has been exploited in the wild.

### Patches

We have released [Pomerium v0.27.1](https://github.com/pomerium/pomerium/releases/tag/v0.27.1) which includes a fix for the JWT validation logic. All affected users are strongly encouraged to upgrade to this version.

### Workarounds

If you cannot upgrade immediately, consider the following mitigations:

- Network access controls: Restrict access to the Pomerium internal gRPC API by configuring your network firewall or security groups to limit access to trusted sources only. Ensure that the port specified in the [`grpc_address`](https://www.pomerium.com/docs/reference/grpc#grpc-address) setting is not exposed to unauthorized networks.

- _For Pomerium Zero deployments only:_ As of Pomerium v0.26.0, you can disable the gRPC API listener by setting `grpc_address: ""` in your YAML configuration file. In all-in-one mode, Pomerium does not require the internal gRPC API to be exposed beyond localhost.

### For more information
If you have questions or need further assistance:

- Open an issue in the [pomerium/pomerium](https://github.com/pomerium/pomerium/issues) repository.
- Contact us at [security@pomerium.com](mailto:security@pomerium.com).

## References
- https://github.com/pomerium/pomerium/security/advisories/GHSA-r7rh-jww5-5fjr
- https://nvd.nist.gov/vuln/detail/CVE-2024-47616
- https://github.com/pomerium/pomerium/commit/e018cf0fc0979d2abe25ff705db019feb7523444
- https://github.com/pomerium/pomerium
- https://github.com/pomerium/pomerium/releases/tag/v0.27.1
- https://pkg.go.dev/vuln/GO-2024-3179
