# [M] url-parse Incorrectly parses URLs that include an '@'

## Summary
Severity: Medium
Advisory: GHSA-8v38-pw62-9cw2
CVE: CVE-2022-0639
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-18
Source: https://github.com/advisories/GHSA-8v38-pw62-9cw2
Type: github-advisory

## Affected
- npm: `url-parse` — affected >=1.0.0 <1.5.7

## Details
A specially crafted URL with an '@' sign but empty user info and no hostname, when parsed with url-parse, url-parse will return the incorrect href. In particular,

```js
parse(\"http://@/127.0.0.1\")
```
Will return:
```yaml
{
 slashes: true,
 protocol: 'http:',
 hash: '',
 query: '',
 pathname: '/127.0.0.1',
 auth: '',
 host: '',
 port: '',
 hostname: '',
 password: '',
 username: '',
 origin: 'null',
 href: 'http:///127.0.0.1'
 }
```
If the 'hostname' or 'origin' attributes of the output from url-parse are used in security decisions and the final 'href' attribute of the output is then used to make a request, the decision may be incorrect.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0639
- https://github.com/unshiftio/url-parse/commit/ef45a1355375a8244063793a19059b4f62fc8788
- https://github.com/unshiftio/url-parse
- https://huntr.dev/bounties/83a6bc9a-b542-4a38-82cd-d995a1481155
- https://lists.debian.org/debian-lts-announce/2023/02/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/12/msg00024.html
