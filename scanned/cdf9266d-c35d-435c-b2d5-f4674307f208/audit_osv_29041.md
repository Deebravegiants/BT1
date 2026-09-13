# [C] CVE-2024-39236

## Summary
Severity: Critical
Advisory: CVE-2024-39236
Aliases: GHSA-9v2f-6vcg-3hgv, PYSEC-2024-274
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-01
Source: https://osv.dev/vulnerability/CVE-2024-39236
Type: osv

## Details
Gradio v4.36.1 was discovered to contain a code injection vulnerability via the component /gradio/component_meta.py. This vulnerability is triggered via a crafted input. NOTE: the supplier disputes this because the report is about a user attacking himself.

## References
- https://github.com/Aaron911/PoC/blob/main/Gradio.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39236.json
- https://github.com/advisories/GHSA-9v2f-6vcg-3hgv
- https://nvd.nist.gov/vuln/detail/CVE-2024-39236
- https://github.com/gradio-app/gradio/issues/8853
