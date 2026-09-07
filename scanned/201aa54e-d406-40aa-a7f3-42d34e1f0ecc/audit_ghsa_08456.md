# [M] @cyclonedx/cdxgen: Docker registry auth substring match forwards credentials to a different registry

## Summary
Severity: Medium
Advisory: GHSA-qhh4-458h-xwh2
CWE: CWE-346, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-qhh4-458h-xwh2
Type: github-advisory

## Affected
- npm: `@cyclonedx/cdxgen` — affected >=9.9.5 <12.3.3

## Details
# Docker registry auth substring match forwards credentials to a different registry

## Repository

`cdxgen/cdxgen`

## Affected product/package

- Ecosystem: npm
- Package: `@cyclonedx/cdxgen`
- Reviewed tree version: `12.3.3`
- Reviewed commit: `b1e179869fd7c6032c3d483c3f7bd4d7154ec22b`
- Affected file: `lib/managers/docker.js`
- Affected from: v9.9.5

The Single Executable Applications (SEA) binaries and container images are also affected.

## Weakness

CWE-522 / CWE-346.

## Summary

When cdxgen scans or pulls container images through the Docker daemon API, it builds an `X-Registry-Auth` header from Docker credentials in `DOCKER_CONFIG/config.json`. The credential selection logic matches configured registry keys with substring checks:

```js
if (forRegistry && !serverAddress.includes(forRegistry)) {
  continue;
}
```

This is not an origin-safe registry comparison. For example, credentials configured for `private-registry.example.com` are selected for a requested image under `registry.example.com`, because:

```js
"private-registry.example.com".includes("registry.example.com") === true
```

The selected credentials are then serialized into `X-Registry-Auth` for the Docker API pull request targeting the requested registry.

## Reproduction

Use the attached/local proof:

```sh
node submissions/github-gsa/cdxgen-docker-registry-auth-substring-forwarding/evidence/cdxgen_docker_registry_auth_substring_probe.mjs
```

The proof is fully local. It creates a temporary Docker config containing credentials for `private-registry.example.com`, starts a localhost mock Docker API endpoint, sets `DOCKER_HOST` to that endpoint, then calls cdxgen's exported Docker request path for a pull from `registry.example.com`.

Observed vulnerable output:

```json
{
  "decision": "GO",
  "dockerConfigAuthHost": "private-registry.example.com",
  "requestedRegistry": "registry.example.com",
  "substringMatch": true,
  "dockerApiUrl": "/images/create?fromImage=registry.example.com/team/app:latest",
  "headerPresent": true,
  "decodedHeader": {
    "username": "trusted-user",
    "password": "trusted-pass",
    "serveraddress": "private-registry.example.com"
  }
}
```

## Impact

If an operator has Docker credentials for a private registry and uses cdxgen to scan an image from a different registry whose hostname is a substring of that private registry hostname, cdxgen can attach the private registry credentials to the Docker pull request for the different registry.

In a realistic attack, an attacker who controls or can observe the requested registry can induce a victim to scan an image from that registry. The Docker daemon API receives an `X-Registry-Auth` payload containing credentials for the victim's private registry but associated with the attacker-requested pull. This is a credential forwarding/misbinding issue in cdxgen's container image handling.


## References

Functions `normalizeRegistryHost` and `registriesMatch` added to normalize and perform strict host matching.

Fix PR: https://github.com/cdxgen/cdxgen/pull/3964

Researcher: Francesco SabiuResearcher: Francesco Sabiu

## References
- https://github.com/cdxgen/cdxgen/security/advisories/GHSA-qhh4-458h-xwh2
- https://github.com/cdxgen/cdxgen
