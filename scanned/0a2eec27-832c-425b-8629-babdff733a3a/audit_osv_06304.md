# [H] BIT-libpython-2023-36632

## Summary
Severity: High
Advisory: BIT-libpython-2023-36632
Aliases: BIT-python-2023-36632, BIT-python-min-2023-36632, CVE-2023-36632, PSF-2023-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-36632
Type: osv

## Affected
- Bitnami: `libpython` — affected >=0 <3.11.5

## Details
The legacy email.utils.parseaddr function in Python through 3.11.4 allows attackers to trigger "RecursionError: maximum recursion depth exceeded while calling a Python object" via a crafted argument. This argument is plausibly an untrusted value from an application's input data that was supposed to contain a name and an e-mail address. NOTE: email.utils.parseaddr is categorized as a Legacy API in the documentation of the Python email package. Applications should instead use the email.parser.BytesParser or email.parser.Parser class. NOTE: the vendor's perspective is that this is neither a vulnerability nor a bug. The email package is intended to have size limits and to throw an exception when limits are exceeded; they were exceeded by the example demonstration code.

## References
- https://docs.python.org/3/library/email.html
- https://docs.python.org/3/library/email.utils.html
- https://github.com/Daybreak2019/PoC_python3.9_Vul/blob/main/RecursionError-email.utils.parseaddr.py
- https://github.com/python/cpython/issues/103800
- https://nvd.nist.gov/vuln/detail/CVE-2023-36632
