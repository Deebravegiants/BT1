# [H] Local file inclusion in gradio

## Summary
Severity: High
Advisory: GHSA-6v6g-j5fq-hpvw
CVE: CVE-2024-4941
CWE: CWE-20, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-6v6g-j5fq-hpvw
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <4.31.3

## Details
A local file inclusion vulnerability exists in the JSON component of gradio-app/gradio and was discovered in version 4.25. The vulnerability arises from improper input validation in the `postprocess()` function within `gradio/components/json_component.py`, where a user-controlled string is parsed as JSON. If the parsed JSON object contains a `path` key, the specified file is moved to a temporary directory, making it possible to retrieve it later via the `/file=..` endpoint. This issue is due to the `processing_utils.move_files_to_cache()` function traversing any object passed to it, looking for a dictionary with a `path` key, and then copying the specified file to a temporary directory. The vulnerability can be exploited by an attacker to read files on the remote system, posing a significant security risk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4941
- https://github.com/gradio-app/gradio/commit/ee1e2942e0a1ae84a08a05464e41c8108a03fa9c
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2024-184.yaml
- https://huntr.com/bounties/39889ce1-298d-4568-aecd-7ae40c2ca58e
