# [H] ComfyUI: Path traversal in /experiment/models/preview allows arbitrary image file read

## Summary
Severity: High
Advisory: CVE-2026-56671
Aliases: GHSA-pj59-g5vv-74q4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-56671
Type: osv

## Details
ComfyUI is a modular diffusion model GUI, api and backend with a graph/nodes interface. Prior to 0.28.0, get_model_preview in app/model_manager.py joins an unrestricted filename route capture to a selected model directory without a containment check, allowing an unauthenticated remote attacker to use traversal, encoded traversal, absolute paths, or an unbounded path_index to read image-decodable files and enumerate host paths. get_model_preview (app/model_manager.py) built the path with os.path.join(folder, filename) where filename is an unrestricted {filename:.*} route capture. Literal ../, percent-encoded %2e%2e%2f, and absolute paths all escaped the model directory; path_index was also unbounded. The target file is piped through Pillow and re-encoded as WEBP, so disclosure is limited to image-decodable files plus a file-existence/enumeration oracle (and internal-path leakage via path_index errors). This issue is fixed in version 0.28.0.

## References
- https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56671.json
- https://github.com/Comfy-Org/ComfyUI/security/advisories/GHSA-pj59-g5vv-74q4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56671
- https://github.com/Comfy-Org/ComfyUI/pull/14734
