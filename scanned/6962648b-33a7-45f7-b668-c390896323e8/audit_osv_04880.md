# [H] Git alllows arbitrary file writes via bundle-uri parameter injection

## Summary
Severity: High
Advisory: BIT-git-2025-48385
Aliases: CVE-2025-48385, GHSA-m98c-vgpc-9655
Ecosystem: Bitnami
Published: 2025-07-10
Source: https://osv.dev/vulnerability/BIT-git-2025-48385
Type: osv

## Affected
- Bitnami: `git` — affected >=0 <2.50.1

## Details
Git is a fast, scalable, distributed revision control system with an unusually rich command set that provides both high-level operations and full access to internals. When cloning a repository Git knows to optionally fetch a bundle advertised by the remote server, which allows the server-side to offload parts of the clone to a CDN. The Git client does not perform sufficient validation of the advertised bundles, which allows the remote side to perform protocol injection. This protocol injection can cause the client to write the fetched bundle to a location controlled by the adversary. The fetched content is fully controlled by the server, which can in the worst case lead to arbitrary code execution. The use of bundle URIs is not enabled by default and can be controlled by the bundle.heuristic config option. Some cases of the vulnerability require that the adversary is in control of where a repository will be cloned to. This either requires social engineering or a recursive clone with submodules. These cases can thus be avoided by disabling recursive clones. This vulnerability is fixed in v2.43.7, v2.44.4, v2.45.4, v2.46.4, v2.47.3, v2.48.2, v2.49.1, and v2.50.1.

## References
- https://github.com/git/git/security/advisories/GHSA-m98c-vgpc-9655
- https://nvd.nist.gov/vuln/detail/CVE-2025-48385
- http://www.openwall.com/lists/oss-security/2025/07/08/4
