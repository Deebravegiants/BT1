# [C] ZenML 0.94.6 Remote Code Execution via CloudpickleMaterializer

## Summary
Severity: Critical
Advisory: CVE-2026-68772
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-68772
Type: osv

## Details
ZenML 0.94.6 contains a remote code execution vulnerability in the CloudpickleMaterializer component that allows attackers with write access to a shared artifact store to execute arbitrary code by planting a malicious pickle file. Attackers can replace a stored artifact.pkl file with a crafted cloudpickle payload containing a malicious __reduce__ method, which executes arbitrary system commands when any user or pipeline materializes the artifact through the unsanitized cloudpickle.load() call in cloudpickle_materializer.py.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68772.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68772
- https://www.vulncheck.com/advisories/zenml-remote-code-execution-via-cloudpicklematerializer
- https://github.com/zenml-io/zenml/pull/5103
- https://github.com/zenml-io/zenml/commit/bbf8496d049a7e23800bc31b87b10b4fefbebe18
- https://github.com/zenml-io/zenml
