# [C] Files on the host computer can be accessed from the Gradio interface

## Summary
Severity: Critical
Advisory: GHSA-rhq2-3vr9-6mcr
CVE: CVE-2021-43831
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-rhq2-3vr9-6mcr
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <2.5.0

## Details
### Impact
This is a vulnerability that affects anyone who creates and publicly shares Gradio interfaces using `gradio<2.4.8`. Because of the way that static files were being served, someone who generated a public Gradio link and shared it with others would potentially be exposing the files on the computer that generated the link, while the link was active. An attacker would be able to view the contents of a file on the computer if they knew the exact relative filepath. We do not have any evidence that this was ever exploited, but we treated the issue seriously and immediately took steps to mitigate it (see below)

### Response
1. We worked with @haby0 to immediately patch the issue and released a new version, `gradio 2.5.0`, within 24 hours of the issue being brought to our attention 
2. We enabled a notification that is printed to anyone using an older version of gradio telling them to upgrade (see screenshot below)
3. We expanded our test suite to test for this vulnerability ensuring that our patch does not get reverted in future releases of `gradio`

![image](https://user-images.githubusercontent.com/1778297/146251425-f36b519b-6d4a-4dfb-8d89-c1ed005979d3.png)

### Patches
The problem has been patched in `gradio>=2.5.0`.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-rhq2-3vr9-6mcr
- https://nvd.nist.gov/vuln/detail/CVE-2021-43831
- https://github.com/gradio-app/gradio/commit/41bd3645bdb616e1248b2167ca83636a2653f781
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2021-873.yaml
