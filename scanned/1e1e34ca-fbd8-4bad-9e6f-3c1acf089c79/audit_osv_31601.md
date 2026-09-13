# [M] Ollama Multi-Modal Model Image Processing NULL Pointer Dereference

## Summary
Severity: Medium
Advisory: CVE-2025-15514
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2025-15514
Type: osv

## Details
Ollama 0.11.5-rc0 through current version 0.13.5 contain a null pointer dereference vulnerability in the multi-modal model image processing functionality. When processing base64-encoded image data via the /api/chat endpoint, the application fails to validate that the decoded data represents valid media before passing it to the mtmd_helper_bitmap_init_from_buf function. This function can return NULL for malformed input, but the code does not check this return value before dereferencing the pointer in subsequent operations. A remote attacker can exploit this by sending specially crafted base64 image data that decodes to invalid media, causing a segmentation fault and crashing the runner process. This results in a denial of service condition where the model becomes unavailable to all users until the service is restarted.

## References
- https://https://github.com/ollama/ollama
- https://ollama.com/
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-15514.json
- https://access.redhat.com/security/cve/CVE-2025-15514
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15514.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15514
- https://www.vulncheck.com/advisories/ollama-multi-modal-image-processing-null-pointer-dereference
- https://bugzilla.redhat.com/show_bug.cgi?id=2428828
- https://github.com/ollama/ollama
- https://huntr.com/bounties/172df98b-07cd-41ea-a628-366f8cd525c0
