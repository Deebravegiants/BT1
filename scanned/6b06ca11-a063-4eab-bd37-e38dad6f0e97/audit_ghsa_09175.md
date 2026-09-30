# [C] imgaug contains an insecure deserialization vulnerability in BackgroundAugmenter class within multicore.py module

## Summary
Severity: Critical
Advisory: GHSA-g82g-j283-hj97
CVE: CVE-2026-31235
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-g82g-j283-hj97
Type: github-advisory

## Affected
- PyPI: `imgaug` — affected >=0

## Details
The imgaug library thru 0.4.0 contains an insecure deserialization vulnerability in its BackgroundAugmenter class within the multicore.py module. The class uses Python's pickle module to deserialize data received via a multiprocessing queue in the _augment_images_worker() method without any safety checks. An attacker who can influence the data placed into this queue (e.g., through social engineering, malicious input scripts, or a compromised shared queue) can provide a malicious pickle payload. When deserialized, this payload can execute arbitrary code in the context of the worker process, leading to remote or local code execution depending on the deployment scenario.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31235
- https://github.com/aleju/imgaug
- https://www.notion.so/CVE-2026-31235-35d1e139318881efb701d814228424a9
