# [H] ghost vulnerable to unauthorized newsletter modification via improper access controls

## Summary
Severity: High
Advisory: GHSA-9gh8-wp53-ccc6
CVE: CVE-2022-41654
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2022-11-28
Source: https://github.com/advisories/GHSA-9gh8-wp53-ccc6
Type: github-advisory

## Affected
- npm: `ghost` — affected >=5.0.0 <5.22.7
- npm: `ghost` — affected >=4.46.0 <4.48.8

## Details
### Impact

On sites where members is enabled (this is the default) it is possible for members (unprivileged users) to make changes to newsletter settings. This gives unprivileged users the ability to view and change settings they were not intended to have access to. They are not able to escalate their privileges permanently or get access to further information. This issue was caused by a gap in our API validation for nested objects.

Ghost(Pro) has already been patched. We can find no evidence that the issue was exploited on Ghost(Pro) prior to the patch being added.

Self-hosters are impacted if running Ghost a version between v4.46.0 and v4.48.7 or any version of v5 prior to v5.22.7. Immediate action should be taken to secure your site - see patches & workarounds below.

### Patches
-  v4.48.8 / v5.22.7 are patched for all known exploits.
-  v4.48.9 / v5.24.1 contain deeper fixes to the API to close the potential for this vulnerability to appear elsewhere or regress 

### Workarounds
The known exploit can be prevented by [disabling members](https://ghost.org/help/can-i-disable-memberships/) until an update can be performed.

### References
- [forum post](https://forum.ghost.org/t/security-update-available-for-ghost-4-x-and-4-x/34475)

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@ghost.org](mailto:security@ghost.org)

---

Credits: Dave McDaniel and other members of [Cisco Talos](https://talosintelligence.com/vulnerability_reports)

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-9gh8-wp53-ccc6
- https://nvd.nist.gov/vuln/detail/CVE-2022-41654
- https://forum.ghost.org/t/security-update-available-for-ghost-4-48-7-and-5-22-6/34475
- https://github.com/TryGhost/Ghost
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1624
