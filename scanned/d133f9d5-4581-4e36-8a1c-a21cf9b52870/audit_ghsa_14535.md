# [C] jeecg-boot vulnerable to improper authentication 

## Summary
Severity: Critical
Advisory: GHSA-6rfv-h5v8-cj7g
CVE: CVE-2023-1784
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-31
Source: https://github.com/advisories/GHSA-6rfv-h5v8-cj7g
Type: github-advisory

## Affected
- Maven: `org.jeecgframework.boot:jeecg-boot-parent` — affected >=0

## Details
A vulnerability was found in jeecg-boot 3.5.0 that affects some unknown processing of the component API Documentation. The manipulation leads to improper authentication because the software does not prove or insufficiently proves that an identity claim is correct when an actor claims to have a given identity. The attack may be initiated remotely and the exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1784
- https://github.com/jeecgboot/jeecg-boot
- https://note.youdao.com/ynoteshare/index.html?id=7eb8fc804ea3544d8add43749a09173e
- https://vuldb.com/?ctiid.224699
- https://vuldb.com/?id.224699
