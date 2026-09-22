# [C] CVE-2026-15969

## Summary
Severity: Critical
Advisory: CVE-2026-15969
Aliases: GHSA-2wvm-gjg7-5jfm
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15969
Type: osv

## Details
SGLang contains an unauthenticated RCE in /load_lora_adapter_from_tensors via bypass of SafeUnpickler’s incomplete denylist, allowing arbitrary command execution through crafted base64-encoded pickle payloads.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15969.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-2wvm-gjg7-5jfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-15969
