# [M] "catalog's registry v2 api exposed on unauthenticated path in Harbor"

## Summary
Severity: Medium
Advisory: GHSA-38r5-34mr-mvm7
CVE: CVE-2020-29662
CWE: CWE-287, CWE-319
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-12
Source: https://github.com/advisories/GHSA-38r5-34mr-mvm7
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=0 <2.0.5
- Go: `github.com/goharbor/harbor` — affected >=2.1.0 <2.1.2

## Details
### **Impact**
Javier Provecho, member of the TCCT (Telefonica Cloud & Cybersecurity Tech better known as ElevenPaths) SRE team discovered a vulnerability regarding Harbor’s v2 API.

The catalog’s registry v2 api is exposed on an unauthenticated path. The current catalog API path is served at the following path and it requires to be authenticated as an admin.

"GET /v2/_catalog"

However, the authorization can be bypassed by using the following path

"GET /v2/_catalog/"

### **Patches**
If your product uses the affected releases of Harbor, update to either version v2.1.2 or v2.0.5 to fix this issue immediately

https://github.com/goharbor/harbor/releases/tag/v2.1.2
https://github.com/goharbor/harbor/releases/tag/v2.0.5

### **Workarounds**
If you cannot access a patched release, it can be mitigated by disabling that API. For example, redirecting it to a 404 sink hole in the ingress.

### **For more information**
If you have any questions or comments about this advisory, contact cncf-harbor-security@lists.cncf.io
View our security policy at https://github.com/goharbor/harbor/security/policy
https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-29662

## References
- https://github.com/goharbor/harbor/security/advisories/GHSA-38r5-34mr-mvm7
- https://nvd.nist.gov/vuln/detail/CVE-2020-29662
- https://github.com/goharbor/harbor/pull/13676
- https://github.com/goharbor/harbor/commit/3481722f140e1fdf6e6d290b0cd5c86e509feed4
- https://github.com/goharbor/harbor/commit/c7c409a8e5a8b3fd42841dda84759c9d77977853
- https://github.com/goharbor/harbor/releases/tag/v2.0.5
- https://github.com/goharbor/harbor/releases/tag/v2.1.2
