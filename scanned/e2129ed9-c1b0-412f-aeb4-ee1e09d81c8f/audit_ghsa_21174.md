# [H] October CMS upload process vulnerable to RCE via Race Condition

## Summary
Severity: High
Advisory: GHSA-8v7h-cpc2-r8jp
CVE: CVE-2022-24800
CWE: CWE-362
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-8v7h-cpc2-r8jp
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=0 <1.0.476
- Packagist: `october/system` — affected >=1.1.0 <1.1.12
- Packagist: `october/system` — affected >=2.0.0 <2.2.15

## Details
### Impact

This advisory affects plugins that expose the `October\Rain\Database\Attach\File::fromData` as a public interface. This vulnerability does not affect vanilla installations of October CMS since this method is not exposed or used by the system internally or externally.

When the developer allows the user to specify their own filename in the `fromData` method, an unauthenticated user can perform remote code execution (RCE) by exploiting a race condition in the temporary storage directory.

### Patches

The issue has been patched in Build 476 (v1.0.476) and v1.1.12 and v2.2.15.

### Workarounds

Apply https://github.com/octobercms/library/commit/fe569f3babf3f593be2b1e0a4ae0283506127a83 to your installation manually if unable to upgrade to Build 476 (v1.0.476) or v1.1.12 or v2.2.15.

### References

Credits to:
- DucNT, HungTD and GiangVQ from RedTeam@VNG Security Response Center.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-8v7h-cpc2-r8jp
- https://nvd.nist.gov/vuln/detail/CVE-2022-24800
- https://github.com/octobercms/library/commit/fe569f3babf3f593be2b1e0a4ae0283506127a83
- https://github.com/octobercms/october
