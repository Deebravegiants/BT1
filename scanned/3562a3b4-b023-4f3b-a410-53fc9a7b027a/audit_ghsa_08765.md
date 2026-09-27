# [H] dssrf: every IPv6 category bypasses is_url_safe

## Summary
Severity: High
Advisory: GHSA-8p33-q827-ghj5
CVE: CVE-2026-44232
CWE: CWE-791
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-8p33-q827-ghj5
Type: github-advisory

## Affected
- npm: `dssrf` — affected >=0 <1.0.3

## Details
A vulnerability on dssrf allow, an attacker to use, one of them following ipv6

```rust
Input	Category
http://[::1]/	IPv6 loopback
http://[fc00::1]/	IPv6 ULA
http://[fe80::1]/	IPv6 link-local
http://[::ffff:127.0.0.1]/	IPv4-mapped loopback
http://[::ffff:169.254.169.254]/	IPv4-mapped IMDS
http://[::ffff:100.64.0.1]/	IPv4-mapped CGNAT
http://[64:ff9b::7f00:1]/	NAT64 well-known prefix
http://[64:ff9b:1::1]/	NAT64 local-use (RFC 8215)
http://[5f00::1]/	SRv6 SID (RFC 9602)
http://[3fff::1]/	IPv6 documentation (RFC 9637)
http://[fec0::1]/	IPv6 site-local (deprecated, RFC 3879)
http://[::127.0.0.1]/	IPv4-compatible IPv6
```

one of those to bypass dssrf and the attacker get **SSRF**, we claim that ipv6 disabled entirely that is wrong on our documentation

### POC

```bash
mkdir dssrf-poc && cd dssrf-poc
npm init -y >/dev/null
npm install dssrf@^1.0.2
cat > audit.js <<'EOF'
const dssrf = require('dssrf');
const cases = [
  ['http://[::1]/',                         'IPv6 loopback'],
  ['http://[fc00::1]/',                     'IPv6 ULA'],
  ['http://[fe80::1]/',                     'IPv6 link-local'],
  ['http://[::ffff:127.0.0.1]/',            'IPv4-mapped loopback'],
  ['http://[::ffff:169.254.169.254]/',      'IPv4-mapped IMDS'],
  ['http://[64:ff9b::7f00:1]/',             'NAT64 well-known + 127.0.0.1'],
  ['http://[64:ff9b:1::1]/',                'NAT64 local-use (RFC 8215)'],
  ['http://[5f00::1]/',                     'SRv6 SID (RFC 9602)'],
  ['http://[fec0::1]/',                     'IPv6 site-local deprecated'],
  ['http://127.0.0.1/',                     'IPv4 loopback (control)'],
  ['http://10.0.0.1/',                      'IPv4 RFC1918 (control)'],
  ['http://8.8.8.8/',                       'PUBLIC IPv4 (control)'],
];
(async () => {
  for (const [url, label] of cases) {
    const safe = await dssrf.is_url_safe(url);
    console.log(`${safe ? '✓ALLOW' : '·block'}  ${url.padEnd(40)}  ${label}`);
  }
})();
EOF
node audit.js
```

### Credit
Million Thank's to <brmenna@gmail.com> for reporting that responsibly.

### Update
Users need to update from now to dssrf 1.0.3

### Lessons Learned
AS we see in the past and today, a lot of advisories or cves bypasses uses IPv6, and IPv6 is the weakest link to be configured correctly and rarely properly tested, Since we blocked ipv4, our ipv6 blocking logic completly broken and never works

## References
- https://github.com/HackingRepo/dssrf-js/security/advisories/GHSA-8p33-q827-ghj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44232
- https://github.com/HackingRepo/dssrf-js
