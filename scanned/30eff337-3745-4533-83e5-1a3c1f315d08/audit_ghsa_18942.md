# [C] Milvus Proxy has a Critical Authentication Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mhjq-8c7m-3f7p
CVE: CVE-2025-64513
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-mhjq-8c7m-3f7p
Type: github-advisory

## Affected
- Go: `github.com/milvus-io/milvus` — affected >=0.10.4 <2.4.24
- Go: `github.com/milvus-io/milvus` — affected >=2.5.0 <2.5.21
- Go: `github.com/milvus-io/milvus` — affected >=2.6.0 <2.6.5
- Go: `github.com/milvus-io/milvus` — affected >=0 <0.10.3-0.20251107071934-6102f001a971

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
An unauthenticated attacker can exploit this vulnerability to bypass all authentication mechanisms in the Milvus Proxy component, gaining full administrative access to the Milvus cluster.
This grants the attacker the ability to read, modify, or delete data, and to perform privileged administrative operations such as database or collection management.
All users running affected Milvus versions are strongly advised to upgrade immediately.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
This issue has been fixed in the following versions:
	•	Milvus 2.4.24
	•	Milvus 2.5.21
	•	Milvus 2.6.5

Users should upgrade to these patched versions or later to mitigate the vulnerability.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
If immediate upgrade is not possible, a temporary mitigation can be applied by removing the sourceID header from all incoming requests at the gateway, API gateway, or load balancer level before they reach the Milvus Proxy.
This prevents attackers from exploiting the authentication bypass behavior.

### References
_Are there any links users can visit to find out more?_

The following pull requests contain the fixes for the affected Milvus branches:
	•	[Fix for 2.4 branch](https://github.com/milvus-io/milvus/pull/45391)￼
	•	[Fix for 2.5 branch](https://github.com/milvus-io/milvus/pull/45383)￼
	•	[Fix for 2.6 branch](https://github.com/milvus-io/milvus/pull/45379)￼

Special thanks to the Volcengine Milvus team at ByteDance(liumingzhe.5689@bytedance.com) for responsibly discovering, reporting, and coordinating the disclosure of this critical authentication bypass vulnerability with the Milvus maintainers.

## References
- https://github.com/milvus-io/milvus/security/advisories/GHSA-mhjq-8c7m-3f7p
- https://nvd.nist.gov/vuln/detail/CVE-2025-64513
- https://github.com/milvus-io/milvus/pull/45379
- https://github.com/milvus-io/milvus/pull/45383
- https://github.com/milvus-io/milvus/pull/45391
- https://github.com/milvus-io/milvus/commit/6102f001a971c8c8055a4a4cae704442d5cab793
- https://github.com/milvus-io/milvus
