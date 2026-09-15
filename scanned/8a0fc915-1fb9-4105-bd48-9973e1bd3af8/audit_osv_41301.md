# [M] Denial of service via exponential certificate policy tree growth in path validation

## Summary
Severity: Medium
Advisory: CVE-2026-59251
Aliases: EEF-CVE-2026-59251, GHSA-622p-qfh6-c352
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-59251
Type: osv

## Details
Allocation of resources without limits in Erlang/OTP public_key certificate path validation allows a remote unauthenticated attacker to cause denial of service by sending a crafted X.509 certificate chain during the TLS handshake.

During RFC 5280 policy processing in public_key:pkix_path_validation/3, the certificate policy tree maintained by pubkey_policy_tree grows without an upper bound. When a certificate chain contains M policies per certificate and K certificates, the tree grows on the order of M^K nodes because pubkey_policy_tree:add_leaves/2 and pubkey_policy_tree:add_leaf_siblings/2 extend the tree per policy per certificate. A modest chain with many policies per certificate is enough to pin BEAM schedulers and exhaust the node's memory, taking down the entire VM. The attacker only needs to be able to present a certificate chain to the victim, which is the normal precondition for a TLS handshake, so exploitation succeeds against any incoming or outgoing TLS connection that validates the peer's chain (the default for SSL/TLS clients and mutual-TLS servers).

This is the same vulnerability class as OpenSSL's X509_verify_cert policy tree DoS.

This vulnerability is associated with program files lib/public_key/src/pubkey_policy_tree.erl and program routines pubkey_policy_tree:add_leaves/2 and pubkey_policy_tree:add_leaf_siblings/2.

This issue affects OTP from OTP 26.2 before OTP 29.0.4, OTP 28.5.0.4 and OTP 27.3.4.15, corresponding to public_key from 1.15 before 1.21.4, 1.20.3.4 and 1.17.1.5.

## References
- https://cna.erlef.org/cves/CVE-2026-59251.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-59251
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59251.json
- https://github.com/erlang/otp/security/advisories/GHSA-622p-qfh6-c352
- https://nvd.nist.gov/vuln/detail/CVE-2026-59251
- https://github.com/erlang/otp/commit/f04c6bba38de1cf1b1836a7d9a9fbe239bd939e8
- https://github.com/erlang/otp/commit/f8580fc117098c08165f46c26fd0750c5cfb2a90
- https://github.com/erlang/otp
