# [H] ComfyUI: Path traversal in LoadImage via the /prompt API allows arbitrary file existence probing and image exfiltration

## Summary
Severity: High
Advisory: CVE-2026-56673
Aliases: GHSA-rvxv-29p8-pxgq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-31
Source: https://osv.dev/vulnerability/CVE-2026-56673
Type: osv

## Details
ComfyUI is a modular diffusion model GUI, API, and backend with a graph-and-node interface. Prior to 0.28.0, folder_paths.get_annotated_filepath and exists_annotated_filepath join workflow-controlled annotated filenames to a base directory without a containment check, allowing an unauthenticated crafted POST /prompt workflow using LoadImage or sibling nodes to probe arbitrary host paths and exfiltrate image-format files through /view. LoadImage defines a VALIDATE_INPUTS method, which causes the execution engine to skip COMBO (input-directory) validation. Affected nodes include LoadImage, LoadImageMask, LoadImageOutput, LoadAudio, LoadLatent, LoadVideo, and Load3D. This issue is fixed in version 0.28.0.

## References
- https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.28.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56673.json
- https://github.com/Comfy-Org/ComfyUI/security/advisories/GHSA-rvxv-29p8-pxgq
- https://nvd.nist.gov/vuln/detail/CVE-2026-56673
- https://github.com/Comfy-Org/ComfyUI/pull/14734
