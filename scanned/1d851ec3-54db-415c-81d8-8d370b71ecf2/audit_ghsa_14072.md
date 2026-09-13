# [H] distribution catalog API endpoint can lead to OOM via malicious user input

## Summary
Severity: High
Advisory: GHSA-hqxw-f8mx-cpmw
CVE: CVE-2023-2253
CWE: CWE-475, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-hqxw-f8mx-cpmw
Type: github-advisory

## Affected
- Go: `github.com/docker/distribution` — affected >=0 <2.8.2-beta.1

## Details
### Impact

Systems that run `distribution` built after a specific commit running on memory-restricted environments can suffer from denial of service by a crafted malicious `/v2/_catalog` API endpoint request. 

### Patches

Upgrade to at least 2.8.2-beta.1 if you are running `v2.8.x` release. If you use the code from the main branch, update at least to the commit after [f55a6552b006a381d9167e328808565dd2bf77dc](https://github.com/distribution/distribution/commit/f55a6552b006a381d9167e328808565dd2bf77dc).

### Workarounds

There is no way to work around this issue without patching. Restrict access to the affected API endpoint: see the recommendations section.

### References

`/v2/_catalog` endpoint accepts a parameter to control the maximum amount of records returned (query string: `n`).

When not given the default `n=100` is used.  The server trusts that `n` has an acceptable value, however when using a 
maliciously large value, it allocates an array/slice of `n` of strings before filling the slice with data.

This behaviour was introduced ~7yrs ago [1].

### Recommendation

The `/v2/_catalog` endpoint was designed specifically to do registry syncs with search or other API systems. Such an endpoint would create a lot of load on the backend system, due to overfetch required to serve a request in certain implementations.

Because of this, we strongly recommend keeping this API endpoint behind heightened privilege and avoiding leaving it exposed to the internet.

###  For more information

If you have any questions or comments about this advisory:
* Open an issue in [distribution repository](https://github.com/distribution/distribution)
* Email us at [cncf-distribution-security@lists.cncf.io](mailto:cncf-distribution-security@lists.cncf.io)

[1] [faulty commit](https://github.com/distribution/distribution/blob/b7e26bac741c76cb792f8e14c41a2163b5dae8df/registry/handlers/catalog.go#L45)

## References
- https://github.com/distribution/distribution/security/advisories/GHSA-hqxw-f8mx-cpmw
- https://nvd.nist.gov/vuln/detail/CVE-2023-2253
- https://github.com/distribution/distribution/commit/f55a6552b006a381d9167e328808565dd2bf77dc
- https://bugzilla.redhat.com/show_bug.cgi?id=2189886
- https://github.com/distribution/distribution
- https://lists.debian.org/debian-lts-announce/2023/06/msg00035.html
