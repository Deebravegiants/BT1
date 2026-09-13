# [M] osctrl has Stored Cross-Site Scripting (XSS) in On-Demand Query List

## Summary
Severity: Medium
Advisory: GHSA-4rv8-5cmm-2r22
CVE: CVE-2026-28280
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-28
Source: https://github.com/advisories/GHSA-4rv8-5cmm-2r22
Type: github-advisory

## Affected
- Go: `github.com/jmpsec/osctrl` — affected >=0 <0.5.0

## Details
### Summary
A stored Cross-site Scripting (XSS) vulnerability exists in the `osctrl-admin` on-demand query list. A user with query-level permissions can inject arbitrary JavaScript via the query parameter when running an on-demand query. The payload is stored and executes in the browser of any user (including administrators) who visits the query list page. This can be chained with CSRF token extraction to escalate privileges and take actions as the logged in user.

### Impact
An attacker with query-level permissions (the lowest privilege tier) can execute arbitrary JavaScript in the browsers of all users who view the query list. Depending on their level of access, it can lead to full platform compromise if an administrator executes the payload.

### Patches
Fixed in osctrl `v0.5.0`. Users should upgrade immediately.

### Workarounds
Restrict query-level permissions to trusted users. Monitor query list for suspicious payloads. Review osctrl user accounts for unauthorized administrators.

### References
- https://github.com/jmpsec/osctrl/pull/778
- https://cwe.mitre.org/data/definitions/79.html

### Credits

Leon Johnson and Kwangyun Keum from TikTok USDS JV Offensive Security Operations (Offensive Privacy Team) 

https://github.com/Kwangyun → @Kwangyun

https://github.com/sho-luv → @sho-luv

## References
- https://github.com/jmpsec/osctrl/security/advisories/GHSA-4rv8-5cmm-2r22
- https://nvd.nist.gov/vuln/detail/CVE-2026-28280
- https://github.com/jmpsec/osctrl/pull/778
- https://github.com/jmpsec/osctrl/pull/780
- https://github.com/jmpsec/osctrl
