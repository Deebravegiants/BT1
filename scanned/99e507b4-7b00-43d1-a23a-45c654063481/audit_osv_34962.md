# [H] CVE-2025-66909

## Summary
Severity: High
Advisory: CVE-2025-66909
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-19
Source: https://osv.dev/vulnerability/CVE-2025-66909
Type: osv

## Details
Turms AI-Serving module v0.10.0-SNAPSHOT and earlier contains an image decompression bomb denial of service vulnerability. The ExtendedOpenCVImage class in ai/djl/opencv/ExtendedOpenCVImage.java loads images using OpenCV's imread() function without validating dimensions or pixel count before decompression. An attacker can upload a specially crafted compressed image file (e.g., PNG) that is small when compressed but expands to gigabytes of memory when loaded. This causes immediate memory exhaustion, OutOfMemoryError, and service crash. No authentication is required if the OCR service is publicly accessible. Multiple requests can completely deny service availability.

## References
- https://github.com/Xzzz111/public_cve_report/blob/main/CVE-2025-66909_report.md
- https://github.com/turms-im/turms/blob/develop/turms-ai-serving/src/main/java/ai/djl/opencv/ExtendedOpenCVImage.java#L37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66909.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66909
- https://github.com/turms-im/turms
