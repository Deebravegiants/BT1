# [H] Craft CMS has Cloud Metadata SSRF Protection Bypass via DNS Rebinding

## Summary
Severity: High
Advisory: GHSA-gp2f-7wcm-5fhx
CVE: CVE-2026-27127
CWE: CWE-367
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-02-23
Source: https://github.com/advisories/GHSA-gp2f-7wcm-5fhx
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.23
- Packagist: `craftcms/cms` — affected >=3.5.0 <4.16.19

## Details
## Summary

The SSRF validation in Craft CMS’s GraphQL Asset mutation performs DNS resolution **separately** from the HTTP request. This Time-of-Check-Time-of-Use (TOCTOU) vulnerability enables DNS rebinding attacks, where an attacker’s DNS server returns different IP addresses for validation compared to the actual request.

This is a bypass of the security fix for CVE-2025-68437 ([GHSA-x27p-wfqw-hfcc](https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc)) that allows access to all blocked IPs, not just IPv6 endpoints.

## Severity

Bypass of cloud metadata SSRF protection for all blocked IPs

## Required Permissions

Exploitation requires GraphQL schema permissions for:
- Edit assets in the `<VolumeName>` volume
- Create assets in the `<VolumeName>` volume

These permissions may be granted to:
- Authenticated users with appropriate GraphQL schema access
- Public Schema (if misconfigured with write permissions)

---

## Technical Details

### Vulnerable Code Flow

The code at `src/gql/resolvers/mutations/Asset.php` performs two separate DNS lookups:

```php
// VALIDATION PHASE: First DNS resolution at time T1
private function validateHostname(string $url): bool
{
    $hostname = parse_url($url, PHP_URL_HOST);
    $ip = gethostbyname($hostname);  // DNS Lookup #1 - Returns safe IP

    if (in_array($ip, [
        '169.254.169.254',   // AWS, GCP, Azure IMDS
        '169.254.170.2',     // AWS ECS metadata
        '100.100.100.200',   // Alibaba Cloud
        '192.0.0.192',       // Oracle Cloud
    ])) {
        return false;  // Check passes - IP looks safe
    }
    return true;
}

// ... time gap between validation and request ...

// REQUEST PHASE: Second DNS resolution at time T2 (inside Guzzle)
$response = $client->get($url);  // DNS Lookup #2 - Guzzle resolves DNS AGAIN
                                  // Now returns 169.254.169.254!
```

### Root Cause

Two separate DNS lookups occur:
1. **Validation**: `gethostbyname()` in `validateHostname()`
2. **Request**: Guzzle's internal DNS resolution via libcurl

An attacker controlling a DNS server can return different IPs for each query.

### Bypass Mechanism

```
+-----------------------------------------------------------------------------+
| Attacker's DNS Server: evil.attacker.com                                    |
+-----------------------------------------------------------------------------+
| Query 1 (Validation - T1):                                                  |
|   Request:  A record for evil.attacker.com                                  |
|   Response: 1.2.3.4 (safe IP, TTL: 0)                                       |
|   Result:   Validation PASSES                                               |
+-----------------------------------------------------------------------------+
| Query 2 (Guzzle Request - T2):                                              |
|   Request:  A record for evil.attacker.com                                  |
|   Response: 169.254.169.254 (metadata IP, TTL: 0)                           |
|   Result:   Request goes to blocked IP -> CREDENTIALS STOLEN                |
+-----------------------------------------------------------------------------+
```

---

## Target Endpoints via DNS Rebinding

DNS rebinding allows access to all blocked IPs:

| Target | Rebind To | Impact |
|--------|-----------|--------|
| **AWS IMDS** | `169.254.169.254` | IAM credentials, instance identity |
| **AWS ECS** | `169.254.170.2` | Container credentials |
| **GCP Metadata** | `169.254.169.254` | Service account tokens |
| **Azure Metadata** | `169.254.169.254` | Managed identity tokens |
| **Alibaba Cloud** | `100.100.100.200` | Instance credentials |
| **Oracle Cloud** | `192.0.0.192` | Instance metadata |
| **Internal Services** | `127.0.0.1`, `10.x.x.x` | Internal APIs, databases |

---

### Attack Scenario

1. Attacker sets up DNS server with alternating responses
2. Attacker sends mutation with `url: "http://evil.attacker.com/latest/meta-data/"`
3. First DNS query returns safe IP (e.g., `1.2.3.4`) → validation passes
4. Second DNS query returns metadata IP (`169.254.169.254`) → request to metadata
5. Attacker retrieves credentials from ANY cloud provider
6. **Attacker can now achieve code execution by creating new instances with their SSH key**

---

## Remediation

### Fix: DNS Pinning with CURLOPT_RESOLVE

Pin the DNS resolution - use the same resolved IP for both validation and request:

```php
private function validateHostname(string $url): bool
{
    $hostname = parse_url($url, PHP_URL_HOST);

    // Resolve once
    $ip = gethostbyname($hostname);

    // Validate the resolved IP
    if (in_array($ip, [
        '169.254.169.254', '169.254.170.2',
        '100.100.100.200', '192.0.0.192',
    ])) {
        return false;
    }

    // Store for later use
    $this->pinnedDNS[$hostname] = $ip;

    return true;
}

// When making the request - CRITICAL: Use pinned IP
protected function makeRequest(string $url): ResponseInterface
{
    $hostname = parse_url($url, PHP_URL_HOST);
    $ip = $this->pinnedDNS[$hostname] ?? null;

    $options = [];
    if ($ip) {
        // Force Guzzle/curl to use the SAME IP we validated
        $options['curl'] = [
            CURLOPT_RESOLVE => [
                "$hostname:80:$ip",
                "$hostname:443:$ip"
            ]
        ];
    }

    return $this->client->get($url, $options);
}
```

### Alternative: Single Resolution with Immediate Use

```php
// Resolve to IP and use IP directly in URL
$ip = gethostbyname($hostname);

if (in_array($ip, $blockedIPs)) {
    return false;
}

// Make request directly to IP with Host header
$client->get("http://$ip" . parse_url($url, PHP_URL_PATH), [
    'headers' => [
        'Host' => $hostname
    ]
]);
```

### Additional Mitigations

| Mitigation | Description |
|------------|-------------|
| DNS Pinning (CURLOPT_RESOLVE) | Force same IP for validation and request |
| Single IP-based request | Use resolved IP directly in URL |
| Implement IMDSv2 | Requires token header (infrastructure-level) |
| Network egress filtering | Block metadata IPs at network level |

---

## Resources

- https://github.com/craftcms/cms/commit/a4cf3fb63bba3249cf1e2882b18a2d29e77a8575
- [GHSA-x27p-wfqw-hfcc](https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc) - Original SSRF vulnerability (CVE-2025-68437)
- [DNSrebinder](https://github.com/mogwailabs/DNSrebinder) - Lightweight Python DNS server for testing DNS rebinding vulnerabilities; responds with legitimate IP for first N queries, then rebinds to target IP
- [Singularity DNS Rebinding Tool](https://github.com/nccgroup/singularity)
- [rbndr DNS Rebinding Service](https://github.com/taviso/rbndr)
- [DNS Rebinding Attacks Explained](https://unit42.paloaltonetworks.com/dns-rebinding/)
- [CURLOPT_RESOLVE Documentation](https://curl.se/libcurl/c/CURLOPT_RESOLVE.html)
- OWASP SSRF Prevention Cheat Sheet

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-gp2f-7wcm-5fhx
- https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27127
- https://github.com/craftcms/cms/commit/a4cf3fb63bba3249cf1e2882b18a2d29e77a8575
- https://curl.se/libcurl/c/CURLOPT_RESOLVE.html
- https://github.com/craftcms/cms
- https://github.com/mogwailabs/DNSrebinder
- https://github.com/nccgroup/singularity
- https://github.com/taviso/rbndr
- https://unit42.paloaltonetworks.com/dns-rebinding
