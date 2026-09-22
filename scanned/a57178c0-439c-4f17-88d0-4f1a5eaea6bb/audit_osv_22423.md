# [H] Use after free in Envoy

## Summary
Severity: High
Advisory: CVE-2022-29227
Aliases: BIT-envoy-2022-29227, GHSA-rm2p-qvf6-pvr6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/CVE-2022-29227
Type: osv

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. In versions prior to 1.22.1 if Envoy attempts to send an internal redirect of an HTTP request consisting of more than HTTP headers, there’s a lifetime bug which can be triggered. If while replaying the request Envoy sends a local reply when the redirect headers are processed, the downstream state indicates that the downstream stream is not complete. On sending the local reply, Envoy will attempt to reset the upstream stream, but as it is actually complete, and deleted, this result in a use-after-free. Users are advised to upgrade. Users unable to upgrade are advised to disable internal redirects if crashes are observed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29227.json
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rm2p-qvf6-pvr6
- https://nvd.nist.gov/vuln/detail/CVE-2022-29227
- https://github.com/envoyproxy/envoy/commit/fe7c69c248f4fe5a9080c7ccb35275b5218bb5ab
