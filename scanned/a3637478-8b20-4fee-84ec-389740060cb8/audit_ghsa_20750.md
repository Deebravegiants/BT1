# [C] NVFLARE unsafe deserialization due to Pickle

## Summary
Severity: Critical
Advisory: GHSA-6qv6-q77g-7qm6
CVE: CVE-2022-34668
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-31
Source: https://github.com/advisories/GHSA-6qv6-q77g-7qm6
Type: github-advisory

## Affected
- PyPI: `nvflare` — affected >=0 <2.1.4

## Details
### Impact
NVFLARE contains a vulnerability where deserialization of Untrusted Data due to Pickle usage may allow an unprivileged network attacker to cause Remote Code Execution, Denial Of Service, and Impact to both Confidentiality and Integrity. 

All versions before 2.1.4 are affected. 

CVSS Score = 9.8 
 
[AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H) 


### Patches
 
The patch is included in nvflare==2.1.4 
This new version uses MessagePack instead of Pickle to do serialization and deserialization.  

Some object serializations supported by Pickle are not supported by MessagePack. We have provided out of box support for some built-in NVFLARE objects. For object serializations unsupported by MessagePack, the user will need to convert the objects to numpy or bytes before sending over to remote machines.  The list of supported object types are listed in https://github.com/NVIDIA/NVFlare/blob/2.1/nvflare/fuel/utils/fobs/README.rst 

 
### Workarounds

No workarounds available. 
 
### Additional information 
Issue Found by: Oliver Sellwood (Nintorac) and Elias Hohl

## References
- https://github.com/NVIDIA/NVFlare/security/advisories/GHSA-6qv6-q77g-7qm6
- https://nvd.nist.gov/vuln/detail/CVE-2022-34668
- https://github.com/NVIDIA/NVFlare/commit/6cde16f3f4711583ae4d896dfcc125d25c7d5b0d
- https://github.com/NVIDIA/NVFlare
- https://github.com/pypa/advisory-database/tree/main/vulns/nvflare/PYSEC-2022-257.yaml
- http://packetstormsecurity.com/files/171483/NVFLARE-Unsafe-Deserialization.html
