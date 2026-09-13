# [C] manga-image-translator RCE via Unsafe Pickle Deserialization in Share Model

## Summary
Severity: Critical
Advisory: CVE-2026-10042
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-10042
Type: osv

## Details
manga-image-translator contains a remote code execution vulnerability in the shared API server mode due to unsafe deserialization of untrusted pickle data in the share.py module, where the /execute/{method_name} and /simple_execute/{method_name} endpoints deserialize attacker-controlled HTTP request bodies using pickle.loads(). A remote attacker can supply a crafted pickle payload to these endpoints to execute arbitrary code in the server process, resulting in full container compromise when running in the default Docker deployment as root.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10042.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10042
- https://www.vulncheck.com/advisories/manga-image-translator-rce-via-unsafe-pickle-deserialization-in-share-model
- https://github.com/zyddnys/manga-image-translator/issues/1141
- https://github.com/zyddnys/manga-image-translator/pull/1142
- https://github.com/zyddnys/manga-image-translator/commit/d7441481a7ed3236b4e0456670a9962a8c82d94d
