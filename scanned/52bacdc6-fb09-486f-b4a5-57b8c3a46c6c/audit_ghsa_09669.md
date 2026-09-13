# [M] OpenC3 COSMOS allows arbitrary writes to plugins directory via path-traversed config filenames

## Summary
Severity: Medium
Advisory: GHSA-4jvx-93h3-f45h
CVE: CVE-2026-42085
CWE: CWE-23
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-4jvx-93h3-f45h
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <6.10.5
- RubyGems: `openc3` — affected >=7.0.0.pre.rc1 <7.0.0-rc3

## Details
### Summary
OpenC3 COSMOS contains a design flaw in the `save_tool_config()` function that allows saving tool configuration files at arbitrary locations inside the shared `/plugins` directory tree by supplying crafted configuration filenames. Although the implementation sufficiently mitigates standard path traversal attacks, by canonicalizing filename to an absolute path, all plugins share this same root directory. That enables users to create arbitrary file structures and overwrite existing configuration files within the shared `/plugins` directory.

### Details
In function `save_tool_config()` ([local_mode.rb](https://github.com/OpenC3/cosmos/blob/397abec0d57972881a2e8dc10902d0dce9c27f42/openc3/lib/openc3/utilities/local_mode.rb#L452))  responsible for saving user-supplied tool configuration, the desired saving directory is not sufficiently enforced, instead allowing writes inside entire `OPENC3_LOCAL_MODE_PATH`.

### PoC
1.	Navigate to any tool that enables “Save Configuration” option in left-hand drop-down menu (here Limits Monitor as an example)
2.	Save a new config with path traversal name using “../” sequences to escape desired directory (up to 3 levels high)
3.	Observe new files created in /plugins directory by inspecting docker container directly (`openc3-COSMOS-cmd-tlm-api`) or using Bucket Explorer (`plugin_default`)

<img width="811" height="584" alt="image" src="https://github.com/user-attachments/assets/015a59b4-8b18-4801-aef0-df4831d5c1c3" />
<img width="720" height="664" alt="image" src="https://github.com/user-attachments/assets/8ca4a5b7-ee45-4c3b-99f6-f41f974a74a7" />

### Impact
Modifying the data of other plugins

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-4jvx-93h3-f45h
- https://nvd.nist.gov/vuln/detail/CVE-2026-42085
- https://github.com/OpenC3/cosmos/commit/9957a9fa460c0c0cf5cdbf6a5931bbdd025246a5
- https://github.com/OpenC3/cosmos/commit/e6efccbd148ba0e3361c5891027f2373aa140d42
- https://github.com/OpenC3/cosmos
- https://github.com/OpenC3/cosmos/releases/tag/v6.10.5
- https://github.com/OpenC3/cosmos/releases/tag/v7.0.0-rc3
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2026-42085.yml
