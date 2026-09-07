# [H] TensorFlow has segmentation fault in tfg-translate 

## Summary
Severity: High
Advisory: GHSA-j5w9-hmfh-4cr6
CVE: CVE-2023-25671
CWE: CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-j5w9-hmfh-4cr6
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1

## Details
### Impact
Out-of-bounds access due to mismatched integer type sizes in ValueMap::Manager::GetValueOrCreatePlaceholder. Bug with tfg-translate call to InitMlir. The problem happens with generic functions, as it is already handled for non-generic functions. This is because they, unlike non-generic functions, are using the "old importer". A better long-term solution may be to have the "new importer" handle generic functions.

### Patches
We have patched the issue in GitHub
- commit [760322a71ac9033e122ef1f4b1c62813021e5938](https://github.com/tensorflow/tensorflow/commit/760322a71ac9033e122ef1f4b1c62813021e5938).
- commit [2eedc8f676d2c3b8be9492e547b2bc814c10b367](https://github.com/tensorflow/tensorflow/commit/2eedc8f676d2c3b8be9492e547b2bc814c10b367)

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx

### Affiliation
360 AIVul

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-j5w9-hmfh-4cr6
- https://nvd.nist.gov/vuln/detail/CVE-2023-25671
- https://github.com/tensorflow/tensorflow/commit/2eedc8f676d2c3b8be9492e547b2bc814c10b367
- https://github.com/tensorflow/tensorflow/commit/760322a71ac9033e122ef1f4b1c62813021e5938
- https://github.com/tensorflow/tensorflow
