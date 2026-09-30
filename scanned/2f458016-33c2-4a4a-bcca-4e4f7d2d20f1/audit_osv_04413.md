# [H] Malicious requests can fill up the log files resulting in a deinal of service in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2023-44388
Aliases: CVE-2023-44388, GHSA-89h3-g746-xmwq
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2023-44388
Type: osv

## Affected
- Bitnami: `discourse` — affected unspecified

## Details
Discourse is an open source platform for community discussion. A malicious request can cause production log files to quickly fill up and thus result in the server running out of disk space. This problem has been patched in the 3.1.1 stable and 3.2.0.beta2 versions of Discourse. It is possible to temporarily work around this problem by reducing the `client_max_body_size nginx directive`. `client_max_body_size` will limit the size of uploads that can be uploaded directly to the server.

## References
- http://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size
- https://github.com/discourse/discourse/security/advisories/GHSA-89h3-g746-xmwq
- https://nvd.nist.gov/vuln/detail/CVE-2023-44388
