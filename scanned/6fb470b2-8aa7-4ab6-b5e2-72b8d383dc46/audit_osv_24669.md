# [M] set_term_title command injection in ipython

## Summary
Severity: Medium
Advisory: CVE-2023-24816
Aliases: GHSA-29gw-9793-fvw7, PYSEC-2023-17
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-02-10
Source: https://osv.dev/vulnerability/CVE-2023-24816
Type: osv

## Details
IPython (Interactive Python) is a command shell for interactive computing in multiple programming languages, originally developed for the Python programming language. Versions prior to 8.1.0 are subject to a command injection vulnerability with very specific prerequisites. This vulnerability requires that the function `IPython.utils.terminal.set_term_title` be called on Windows in a Python environment where ctypes is not available. The dependency on `ctypes` in `IPython.utils._process_win32` prevents the vulnerable code from ever being reached in the ipython binary. However, as a library that could be used by another tool `set_term_title` could be called and hence introduce a vulnerability. Should an attacker get untrusted input to an instance of this function they would be able to inject shell commands as current process and limited to the scope of the current process. Users of ipython as a library are advised to upgrade. Users unable to upgrade should ensure that any calls to the `IPython.utils.terminal.set_term_title` function are done with trusted or filtered input.

## References
- https://github.com/ipython/ipython/blob/3f0bf05f072a91b2a3042d23ce250e5e906183fd/IPython/utils/terminal.py#L103-L117
- https://github.com/ipython/ipython/blob/56e6925dfa50e2c7f4a6471547b8176275db7c25/IPython/utils/_process_win32.py#L20
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/24xxx/CVE-2023-24816.json
- https://github.com/ipython/ipython/security/advisories/GHSA-29gw-9793-fvw7
- https://nvd.nist.gov/vuln/detail/CVE-2023-24816
- https://github.com/ipython/ipython/commit/385d69325319a5972ee9b5983638e3617f21cb1f
