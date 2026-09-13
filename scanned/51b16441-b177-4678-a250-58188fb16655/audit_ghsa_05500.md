# [H] ChatterBot Vulnerable to Denial of Service via Database Connection Pool Exhaustion

## Summary
Severity: High
Advisory: GHSA-v4w8-49pv-mf72
CVE: CVE-2026-23842
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-v4w8-49pv-mf72
Type: github-advisory

## Affected
- PyPI: `chatterbot` — affected >=0 <1.2.11

## Details
### Summary
ChatterBot versions up to 1.2.10 are vulnerable to a denial-of-service condition caused by improper database session and connection pool management. Concurrent invocations of the get_response() method can exhaust the underlying SQLAlchemy connection pool, resulting in persistent service unavailability and requiring a manual restart to recover.

### Details
ChatterBot relies on SQLAlchemy for database access and uses a connection pool with default limits. The get_response() method does not enforce concurrency limits, rate limiting, or explicit session lifecycle controls.

When multiple threads concurrently invoke get_response(), database connections are rapidly consumed and not released in a timely manner. This leads to exhaustion of the SQLAlchemy QueuePool, causing subsequent requests to block and eventually fail with a TimeoutError.

This issue can be triggered without authentication in deployments where ChatterBot is exposed as a chatbot service, making it exploitable by remote attackers to cause denial of service.

PoC Video: 
https://github.com/user-attachments/assets/4ee845c4-b847-4854-84ec-4b2fb2f7090f

### PoC
1. Install ChatterBot version 1.2.10.
2. Use the default database configuration (SQLite / SQLAlchemy).
3. Run the following Python script to invoke concurrent requests:

from chatterbot import ChatBot
import threading

bot = ChatBot("dos-test")

def attack():
    bot.get_response("hello")

threads = []
for _ in range(30):
    t = threading.Thread(target=attack)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

4. Observe that the application becomes unresponsive and raises SQLAlchemy TimeoutError exceptions indicating exhaustion of the connection pool.

### Impact
This vulnerability allows an attacker to trigger a denial-of-service condition by exhausting the database connection pool. Once triggered, the chatbot becomes unresponsive to legitimate users and requires a manual restart to restore functionality.

All deployments of ChatterBot version 1.2.10 or earlier that allow concurrent access to the get_response() method are impacted.

## References
- https://github.com/gunthercox/ChatterBot/security/advisories/GHSA-v4w8-49pv-mf72
- https://nvd.nist.gov/vuln/detail/CVE-2026-23842
- https://github.com/gunthercox/ChatterBot/pull/2432
- https://github.com/gunthercox/ChatterBot/commit/de89fe648139f8eeacc998ad4524fab291a378cf
- https://github.com/gunthercox/ChatterBot
- https://github.com/gunthercox/ChatterBot/releases/tag/1.2.11
- https://github.com/user-attachments/assets/4ee845c4-b847-4854-84ec-4b2fb2f7090f
