# [M] Credential exposure when running third-party builders in knative/func

## Summary
Severity: Medium
Advisory: CVE-2022-41939
Aliases: GHSA-5336-2g3f-9g3m
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2022-11-19
Source: https://osv.dev/vulnerability/CVE-2022-41939
Type: osv

## Details
knative.dev/func is is a client library and CLI enabling the development and deployment of Kubernetes functions. Developers using a malicious or compromised third-party buildpack could expose their registry credentials or local docker socket to a malicious `lifecycle` container. This issues has been patched in PR #1442, and is part of release 1.8.1. This issue only affects users who are using function buildpacks from third-parties; pinning the builder image to a specific content-hash with a valid `lifecycle` image will also mitigate the attack.

## References
- https://github.com/knative/func/blob/5ca77d38744d3481cc0b795f607c5859b19588fc/buildpacks/builder.go#L37-L41
- https://github.com/knative/func/releases/tag/knative-v1.8.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41939.json
- https://github.com/knative/func/security/advisories/GHSA-5336-2g3f-9g3m
- https://nvd.nist.gov/vuln/detail/CVE-2022-41939
- https://github.com/knative/func/pull/1442
