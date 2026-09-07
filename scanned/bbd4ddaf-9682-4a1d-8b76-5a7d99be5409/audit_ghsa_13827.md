# [M] TorchServe ZipSlip

## Summary
Severity: Medium
Advisory: GHSA-m2mj-pr4f-h9jp
CVE: CVE-2023-48299
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-m2mj-pr4f-h9jp
Type: github-advisory

## Affected
- PyPI: `torchserve` — affected >=0.1.0 <0.9.0

## Details
### Impact
Using the model/workflow management API, there is a chance of uploading potentially harmful archives that contain files that are extracted to any location on the filesystem that is within the process permissions. Leveraging this issue could aid third-party actors in hiding harmful code in open-source/public models, which can be downloaded from the internet, and take advantage of machines running Torchserve.

### Patches
The ZipSlip issue in TorchServe has been fixed by validating the paths of files contained within a zip archive before extracting them: https://github.com/pytorch/serve/pull/2634

TorchServe release 0.9.0 includes fixes to address the ZipSlip vulnerability:
https://github.com/pytorch/serve/releases/tag/v0.9.0

### References
https://github.com/pytorch/serve/pull/2634
https://github.com/pytorch/serve/releases/tag/v0.9.0

### Credit
We would like to thank Oligo Security for responsibly disclosing this issue.

If you have any questions or comments about this advisory, we ask that you contact AWS Security via our [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/pytorch/serve/security/advisories/GHSA-m2mj-pr4f-h9jp
- https://nvd.nist.gov/vuln/detail/CVE-2023-48299
- https://github.com/pytorch/serve/pull/2634
- https://github.com/pytorch/serve/commit/bfb3d42396727614aef625143b4381e64142f9bb
- https://github.com/pytorch/serve
- https://github.com/pytorch/serve/releases/tag/v0.9.0
