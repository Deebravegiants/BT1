# [H] GeoNode vulnerable to SSRF Bypass to return internal host data

## Summary
Severity: High
Advisory: GHSA-pxg5-h34r-7q8p
CVE: CVE-2023-42439
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-pxg5-h34r-7q8p
Type: github-advisory

## Affected
- PyPI: `GeoNode` — affected >=3.2.0 <4.1.3.post1

## Details
A SSRF vulnerability exists, bypassing existing controls on the software. This can allow a user to request internal services for a full read SSRF, returning any data from the internal network.

the application is using a whitelist, but the whitelist can be bypassed with @ and encoded value of @ (%40) GET /proxy/?url=http://development.demo.geonode.org%40geoserver:8080/geoserver/web 
This will trick the application that the first host is a whitelisted address, but the browser will use @ or %40 as a credential to the host geoserver on port 8080, this will return the data to that host on the response.

![image](https://user-images.githubusercontent.com/35967437/264379628-8cecbc56-be6c-49dc-abe8-0baf8b8695cc.png)

## References
- https://github.com/GeoNode/geonode/security/advisories/GHSA-pxg5-h34r-7q8p
- https://nvd.nist.gov/vuln/detail/CVE-2023-42439
- https://github.com/GeoNode/geonode/commit/79ac6e70419c2e0261548bed91c159b54ff35b8d
- https://github.com/GeoNode/geonode
- https://github.com/GeoNode/geonode/releases/tag/4.1.3
- https://github.com/pypa/advisory-database/tree/main/vulns/geonode/PYSEC-2023-176.yaml
