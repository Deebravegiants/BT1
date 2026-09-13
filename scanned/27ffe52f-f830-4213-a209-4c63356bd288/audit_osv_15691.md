# [H] CVE-2019-18836

## Summary
Severity: High
Advisory: CVE-2019-18836
Aliases: GHSA-3xvf-4396-cj46
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-11
Source: https://osv.dev/vulnerability/CVE-2019-18836
Type: osv

## Details
Envoy 1.12.0 allows a remote denial of service because of resource loops, as demonstrated by a single idle TCP connection being able to keep a worker thread in an infinite busy loop when continue_on_listener_filters_timeout is used."

## References
- https://groups.google.com/forum/#%21forum/envoy-users
- https://blog.envoyproxy.io
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3xvf-4396-cj46
- https://github.com/istio/istio/issues/18229
