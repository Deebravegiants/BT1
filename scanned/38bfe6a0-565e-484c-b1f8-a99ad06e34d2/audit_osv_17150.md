# [C] CVE-2020-13091

## Summary
Severity: Critical
Advisory: CVE-2020-13091
Aliases: PYSEC-2020-73
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-15
Source: https://osv.dev/vulnerability/CVE-2020-13091
Type: osv

## Details
pandas through 1.0.3 can unserialize and execute commands from an untrusted file that is passed to the read_pickle() function, if __reduce__ makes an os.system call. NOTE: third parties dispute this issue because the read_pickle() function is documented as unsafe and it is the user's responsibility to use the function in a secure manner

## References
- https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_pickle.html
- https://github.com/0FuzzingQ/vuln/blob/master/pandas%20unserialize.md
