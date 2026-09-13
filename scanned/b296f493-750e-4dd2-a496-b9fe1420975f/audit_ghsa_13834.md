# [H] Codiad information disclosure vulnerability

## Summary
Severity: High
Advisory: GHSA-2q79-56rq-8v3c
CVE: CVE-2017-20178
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-02-21
Source: https://github.com/advisories/GHSA-2q79-56rq-8v3c
Type: github-advisory

## Affected
- Packagist: `codiad/codiad` — affected >=0 <2.8.1

## Details
A vulnerability was found in Codiad 2.8.0. It has been rated as problematic. Affected by this issue is the function saveJSON of the file components/install/process.php. The manipulation of the argument data leads to information disclosure. The attack may be launched remotely. Upgrading to version 2.8.1 is able to address this issue. The name of the patch is 517119de673e62547ee472a730be0604f44342b5. It is recommended to upgrade the affected component. VDB-221498 is the identifier assigned to this vulnerability. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20178
- https://github.com/Codiad/Codiad/pull/974
- https://github.com/Codiad/Codiad/commit/517119de673e62547ee472a730be0604f44342b5
- https://github.com/Codiad/Codiad
- https://github.com/Codiad/Codiad/releases/tag/v.2.8.1
- https://vuldb.com/?ctiid.221498
- https://vuldb.com/?id.221498
