# [C] Privilege Escalation in kubevirt

## Summary
Severity: Critical
Advisory: GHSA-828r-r2c8-rfw3
CVE: CVE-2020-14316
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-24
Source: https://github.com/advisories/GHSA-828r-r2c8-rfw3
Type: github-advisory

## Affected
- Go: `kubevirt.io/kubevirt` — affected >=0 <0.30.0

## Details
A flaw was found in kubevirt 0.29 and earlier. Virtual Machine Instances (VMIs) can be used to gain access to the host's filesystem. Successful exploitation allows an attacker to assume the privileges of the VM process on the host system. In worst-case scenarios an attacker can read and modify any file on the system where the VMI is running. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14316
- https://github.com/kubevirt/kubevirt/pull/3686
- https://bugzilla.redhat.com/show_bug.cgi?id=1848951
- https://github.com/kubevirt/kubevirt
