# [C] manga-image-translator Shared API Unsafe Deserialization RCE

## Summary
Severity: Critical
Advisory: CVE-2026-26215
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-26215
Type: osv

## Details
manga-image-translator version beta-0.3 and prior in shared API mode contains an unsafe deserialization vulnerability that can lead to unauthenticated remote code execution. The FastAPI endpoints /simple_execute/{method} and /execute/{method} deserialize attacker-controlled request bodies using pickle.loads() without validation. Although a nonce-based authorization check is intended to restrict access, the nonce defaults to an empty string and the check is skipped, allowing remote attackers to execute arbitrary code in the server context by sending a crafted pickle payload.

## References
- https://github.com/zyddnys/manga-image-translator/blob/a537cb12b41daf2065795058c2753d87e73fa0fe/manga_translator/mode/share.py#L112
- https://github.com/zyddnys/manga-image-translator/blob/a537cb12b41daf2065795058c2753d87e73fa0fe/manga_translator/mode/share.py#L130
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26215.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26215
- https://www.vulncheck.com/advisories/manga-image-translator-shared-api-unsafe-deserialization-rce
- https://github.com/zyddnys/manga-image-translator/issues/1116
- https://github.com/zyddnys/manga-image-translator/issues/946
- https://github.com/zyddnys/manga-image-translator
- https://chocapikk.com/posts/2026/manga-image-translator-pickle-rce/
