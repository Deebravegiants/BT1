# [H] ansys-geometry-core OS Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-38jr-29fh-w9vm
CVE: CVE-2024-29189
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-25
Source: https://github.com/advisories/GHSA-38jr-29fh-w9vm
Type: github-advisory

## Affected
- PyPI: `ansys-geometry-core` — affected >=0.3.0 <0.3.3
- PyPI: `ansys-geometry-core` — affected >=0.4.0 <0.4.12

## Details
subprocess call with shell=True identified, security issue.

#### Code

On file [src/ansys/geometry/core/connection/product_instance.py](https://github.com/ansys/pyansys-geometry/blob/52cba1737a8a7812e5430099f715fa2160ec007b/src/ansys/geometry/core/connection/product_instance.py#L403-L428):

```
403 def _start_program(args: List[str], local_env: Dict[str, str]) -> subprocess.Popen:
404     """
405     Start the program where the path is the first item of the ``args`` array argument.
406
407     Parameters
408     ----------
409     args : List[str]
410         List of arguments to be passed to the program. The first list's item shall
411         be the program path.
412     local_env : Dict[str,str]
413         Environment variables to be passed to the program.
414
415     Returns
416     -------
417     subprocess.Popen
418         The subprocess object.
419     """
420      return subprocess.Popen(
421         args,
422         shell=os.name != "nt",
423         stdin=subprocess.DEVNULL,
424         stdout=subprocess.DEVNULL,
425         stderr=subprocess.DEVNULL,
426         env=local_env,
427      )
428 
429 

```

Upon calling this method ``_start_program`` directly, users could exploit its usage to perform malicious operations on the current machine where the script is ran. With this resolution made through #1076 and #1077, we make sure that this method is only called from within the library and we are no longer enabling the ``shell=True`` option.

#### CWE - 78

For more information see https://cwe.mitre.org/data/definitions/78.html

#### More information

Visit https://bandit.readthedocs.io/en/1.7.8/plugins/b602_subprocess_popen_with_shell_equals_true.html to find out more information.

## References
- https://github.com/ansys/pyansys-geometry/security/advisories/GHSA-38jr-29fh-w9vm
- https://nvd.nist.gov/vuln/detail/CVE-2024-29189
- https://github.com/ansys/pyansys-geometry/pull/1076
- https://github.com/ansys/pyansys-geometry/pull/1077
- https://github.com/ansys/pyansys-geometry/commit/902071701c4f3a8258cbaa46c28dc0a65442d1bc
- https://github.com/ansys/pyansys-geometry/commit/f82346b9432b06532e84f3278125f5879b4e9f3f
- https://bandit.readthedocs.io/en/1.7.8/plugins/b602_subprocess_popen_with_shell_equals_true.html
- https://github.com/ansys/pyansys-geometry
- https://github.com/ansys/pyansys-geometry/blob/52cba1737a8a7812e5430099f715fa2160ec007b/src/ansys/geometry/core/connection/product_instance.py#L403-L428
