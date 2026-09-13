# [M] lambdaisland/uri `authority-regex` returns the wrong authority

## Summary
Severity: Medium
Advisory: GHSA-cp4w-6x4w-v2h5
CVE: CVE-2023-28628
CWE: CWE-601, CWE-706
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-27
Source: https://github.com/advisories/GHSA-cp4w-6x4w-v2h5
Type: github-advisory

## Affected
- Maven: `lambdaisland:uri` — affected >=0 <1.14.120

## Details
### Summary
`authority-regex` allows an attacker to send malicious URLs to be parsed by the `lambdaisland/uri` and return the wrong authority. This issue is similar to CVE-2020-8910.

### Details

https://github.com/lambdaisland/uri/blob/d3355fcd3e235238f4dcd37be97787a84e580072/src/lambdaisland/uri.cljc#L9

This regex doesn't handle the backslash (`\`) character in the username correctly, leading to a wrong output.
**Payload:** `https://example.com\\@google.com`
The returned host is `google.com`, but the correct host should be `example.com`.

`urllib3` (Python) and `google-closure-library` (Javascript) return `example.com` as the host. Here the correct (or current) regex used by `google-closure-library`:

https://github.com/google/closure-library/blob/0e567abedb058e9b194a40cfa3ad4c507653bccf/closure/goog/uri/utils.js#L189

### PoC

```
(ns poc.core)
(require '[lambdaisland.uri :refer (uri)])

(def myurl "https://example.com\\@google.com")

(defn -main
  []
   (println myurl)
   (println (:host (uri myurl)))
)
```


### Impact

The library returns the wrong authority, and it can be abused to bypass host restrictions.

### Reference

WHATWG Living URL spec, section 4.4 URL Parsing, host state: https://url.spec.whatwg.org/#url-parsing

## References
- https://github.com/lambdaisland/uri/security/advisories/GHSA-cp4w-6x4w-v2h5
- https://nvd.nist.gov/vuln/detail/CVE-2023-28628
- https://github.com/lambdaisland/uri/commit/f46db3e84846f79e14bfee0101d9c7a872321820
- https://github.com/google/closure-library/blob/0e567abedb058e9b194a40cfa3ad4c507653bccf/closure/goog/uri/utils.js#L189
- https://github.com/lambdaisland/uri
- https://github.com/lambdaisland/uri/blob/d3355fcd3e235238f4dcd37be97787a84e580072/src/lambdaisland/uri.cljc#L9
- https://github.com/lambdaisland/uri/releases/tag/v1.14.120
