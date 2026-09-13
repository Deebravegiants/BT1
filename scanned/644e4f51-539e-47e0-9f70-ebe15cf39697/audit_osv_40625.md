# [C] NVIDIA SIL GEN3C Unauthenticated RCE via Pickle Deserialization in Inference API

## Summary
Severity: Critical
Advisory: CVE-2026-53805
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-53805
Type: osv

## Details
NVIDIA Spatial Intelligence Lab's (SIL) GEN3C contains an unauthenticated remote code execution vulnerability in the inference API server where the /request-inference and /seed-model endpoints deserialize raw HTTP request bodies using Python's pickle.loads() without authentication or input validation. Attackers can supply a crafted payload containing a __reduce__ gadget to the inference API port to achieve remote code execution as the inference process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53805.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53805
- https://www.vulncheck.com/advisories/nvidia-sil-gen3c-unauthenticated-rce-via-pickle-deserialization-in-inference-api
- https://github.com/nv-tlabs/GEN3C/pull/62
- https://github.com/nv-tlabs/GEN3C/pull/63
- https://github.com/nv-tlabs/GEN3C/commit/db2ffe12ced12ddafcec5e0422ee46ce8520746b
- https://github.com/nv-tlabs/GEN3C
