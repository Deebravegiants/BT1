# [M] Broken encryption in EdgeX Foundry

## Summary
Severity: Medium
Advisory: GHSA-6c7m-qwxj-mvhp
CVE: CVE-2021-41278
CWE: CWE-327
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2021-11-19
Source: https://github.com/advisories/GHSA-6c7m-qwxj-mvhp
Type: github-advisory

## Affected
- Go: `github.com/edgexfoundry/app-functions-sdk-go/v2` — affected >=0 <2.1.0
- Go: `github.com/edgexfoundry/app-functions-sdk-go` — affected >=0
- Go: `github.com/edgexfoundry/app-service-configurable` — affected >=0 <2.1.0

## Details
### Summary
Broken encryption in app-functions-sdk “AES” transform in EdgeX Foundry releases prior to Jakarta allows attackers to decrypt messages via unspecified vectors.

### Detailed Description
The app-functions-sdk exports an “aes” transform that user scripts can optionally call to encrypt data in the processing pipeline.  No decrypt function is provided.  Encryption is not enabled by default, but if used, the level of protection may be less than the user may expects due to a broken implementation in https://github.com/edgexfoundry/app-functions-sdk-go/blob/v1.0.0/pkg/transforms/encryption.go 

Version v2.1.0 (EdgeX Foundry Jakarta release and later) of app-functions-sdk-go/v2 deprecates the “aes” transform and provides an improved “aes256” transform in its place.  The broken implementation will remain in a deprecated state until it is removed in the next EdgeX major release to avoid breakage of existing software that depends on the broken implementation.

### Impact
As the broken transform is a library function that is not invoked by default, users who do not use the AES transform in their processing pipelines are unaffected.  Those that are affected are urged to upgrade to the Jakarta EdgeX release and modify processing pipelines to use the new "aes256" transform.

#### Vulnerable go modules
- github.com/edgexfoundry/app-functions-sdk-go  < v2.1.0
- github.com/edgexfoundry/app-functions-sdk-go/v2  < v2.1.0
- github.com/edgexfoundry/app-service-configurable < v2.1.0

#### Vulnerable containers
- https://hub.docker.com/r/edgexfoundry/app-service-configurable >= 2.0.0 < v2.1.0
- https://hub.docker.com/r/edgexfoundry/app-service-configurable-arm64  >= 2.0.0 < 2.1.0
- https://hub.docker.com/r/edgexfoundry/docker-app-service-configurable  < 2.0.0
- https://hub.docker.com/r/edgexfoundry/docker-app-service-configurable-arm64 < 2.0.0 

#### Vulnerable Snaps
- https://snapcraft.io/edgex-app-service-configurable >= 2.0.0 < 2.1.0

### Patches
Upgrade to 2.1.0 version of app-functions-sdk-go/v2, app-service-configurable, and related docker containers shown below and modify user scripts to use the new "aes256" transform in place of the existing "aes" transform.

#### Patched go modules
- github.com/edgexfoundry/app-functions-sdk-go/v2 v2.1.0
- github.com/edgexfoundry/app-service-configurable v2.1.0

Modification of user scripts is necessary for full remediation.

#### Patched containers
- https://hub.docker.com/r/edgexfoundry/app-service-configurable:>=2.1.0
- https://hub.docker.com/r/edgexfoundry/app-service-configurable-arm64:>=2.1.0

Modification of user scripts is necessary for full remediation.

#### Patched Snaps
- https://snapcraft.io/edgex-app-service-configurable >= 2.1.0

Modification of user scripts is necessary for full remediation.

### Workarounds
If unable to upgrade, change the processing pipeline to use an HTTPS (TLS 1.3) endpoint to export and skip encryption.

### References
* [2.0 documentation](https://docs.edgexfoundry.org/2.0/microservices/application/BuiltIn/#aes)
* [2.1 documentation](https://docs.edgexfoundry.org/2.1/microservices/application/BuiltIn/#encryption-deprecated)
* [GitHub issue](https://github.com/edgexfoundry/app-functions-sdk-go/issues/968)

### For more information
If you have any questions or comments about this advisory:
* Contact us in the [Slack #security channel](https://slack.edgexfoundry.org/)
* Open an issue in [edgex-go](https://github.com/edgexfoundry/edgex-go)
* Email us at [EdgeX-TSC-Security@lists.edgexfoundry.org](mailto:EdgeX-TSC-Security@lists.edgexfoundry.org)

## References
- https://github.com/edgexfoundry/app-functions-sdk-go/security/advisories/GHSA-6c7m-qwxj-mvhp
- https://nvd.nist.gov/vuln/detail/CVE-2021-41278
- https://github.com/edgexfoundry/app-functions-sdk-go/commit/8fa13c6388ce76a6b878b54490eac61aa7d81165
- https://github.com/edgexfoundry/app-functions-sdk-go
