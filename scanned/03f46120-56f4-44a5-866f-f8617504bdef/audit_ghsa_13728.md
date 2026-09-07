# [H] Zip slip in mleap

## Summary
Severity: High
Advisory: GHSA-897x-xvj8-42rq
CVE: CVE-2023-5245
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-15
Source: https://github.com/advisories/GHSA-897x-xvj8-42rq
Type: github-advisory

## Affected
- Maven: `ml.combust.mleap:mleap-runtime_2.12` — affected >=0 <0.23.1

## Details
FileUtil.extract() enumerates all zip file entries and extracts each file without validating whether file paths in the archive are outside the intended directory.

When creating an instance of TensorflowModel using the saved_model format and an exported tensorflow model, the apply() function invokes the vulnerable implementation of FileUtil.extract().

Arbitrary file creation can directly lead to code execution

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5245
- https://github.com/combust/mleap/pull/866#issuecomment-1738032225
- https://github.com/combust/mleap
- https://research.jfrog.com/vulnerabilities/mleap-path-traversal-rce-xray-532656
