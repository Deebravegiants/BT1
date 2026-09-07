# [H] Rancher UI has Stored Cross-site Scripting vulnerability

## Summary
Severity: High
Advisory: GHSA-2v2w-8v8c-wcm9
CVE: CVE-2024-52281
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-2v2w-8v8c-wcm9
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.9.0 <2.9.4

## Details
### Impact
A vulnerability has been identified within Rancher UI that allows a malicious actor to perform a Stored XSS attack through the cluster description field.

Please consult the associated  [MITRE ATT&CK - Technique - Drive-by Compromise](https://attack.mitre.org/techniques/T1189/) for further information about this category of attack.

### Patches
The fix introduces new changes in the directives responsible for sanitizing HTML code before rendering. 

We replaced the `v-tooltip` directive with the `v-clean-tooltip` directive.

Patched versions include releases `2.9.4` and `2.10.0`.

### Workarounds
There are no workarounds for this issue. Users are recommended to upgrade, as soon as possible, to a version of /Rancher Manager which contains the fixes.

### Credits
This issue was identified and reported by Bhavin Makwana from Workday’s Cyber Defence Team.

### For more information
If you have any questions or comments about this advisory:
- Reach out to the [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
- Open an issue in the [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
- Verify with our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-2v2w-8v8c-wcm9
- https://nvd.nist.gov/vuln/detail/CVE-2024-52281
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2024-52281
- https://github.com/rancher/rancher
