# [M] Incorrect Authorization in wasmCloud

## Summary
Severity: Medium
Advisory: CVE-2022-21707
Aliases: GHSA-2cmx-rr54-88g5
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2022-01-21
Source: https://osv.dev/vulnerability/CVE-2022-21707
Type: osv

## Details
wasmCloud Host Runtime is a server process that securely hosts and provides dispatch for web assembly (WASM) actors and capability providers. In versions prior to 0.52.2 actors can bypass capability authorization. Actors are normally required to declare their capabilities for inbound invocations, but with this vulnerability actor capability claims are not verified upon receiving invocations. This compromises the security model for actors as they can receive unauthorized invocations from linked capability providers. The problem has been patched in versions `0.52.2` and greater. There is no workaround and users are advised to upgrade to an unaffected version as soon as possible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21707.json
- https://github.com/wasmCloud/wasmcloud-otp/security/advisories/GHSA-2cmx-rr54-88g5
- https://nvd.nist.gov/vuln/detail/CVE-2022-21707
- https://github.com/wasmCloud/wasmcloud-otp/commit/fd07262074b98b06106a31fd1957dc2319d438a5
