# [H] melisplatform/melis-front vulnerable to deserialization of untrusted data

## Summary
Severity: High
Advisory: GHSA-h479-2mv4-5c26
CVE: CVE-2022-39298
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-h479-2mv4-5c26
Type: github-advisory

## Affected
- Packagist: `melisplatform/melis-front` — affected >=0 <5.0.1

## Details
### Impact

Attackers can deserialize arbitrary data on affected versions of `melisplatform/melis-front`, and ultimately leads to the execution of arbitrary PHP code on the system. Conducting this attack does not require authentication.

Users should immediately upgrade to `melisplatform/melis-front` >= 5.0.1.

### Patches

This issue was addressed by restricting allowed classes when deserializing user-controlled data. 

### References

- https://github.com/melisplatform/melis-front/commit/89ae612d5f1f7aa2fb621ee8de27dffe1feb851e

### For more information

If you have any questions or comments about this advisory, you can contact:
- The original reporters, by sending an email to vulnerability.research [at] sonarsource.com;
- The maintainers, by opening an issue on this repository.

## References
- https://github.com/melisplatform/melis-front/security/advisories/GHSA-h479-2mv4-5c26
- https://nvd.nist.gov/vuln/detail/CVE-2022-39298
- https://github.com/melisplatform/melis-front/commit/89ae612d5f1f7aa2fb621ee8de27dffe1feb851e
- https://github.com/melisplatform/melis-front
