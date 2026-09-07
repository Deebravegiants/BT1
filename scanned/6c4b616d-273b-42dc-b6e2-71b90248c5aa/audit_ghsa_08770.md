# [M] Incus has Nil Dereferences on Restore via Malformed YAML

## Summary
Severity: Medium
Advisory: GHSA-x5r6-jr56-89pv
CVE: CVE-2026-41684
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-x5r6-jr56-89pv
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0

## Details
### Summary

### Details
It was found that backup.GetInfo() trusts the inline backup/index.yaml config when present and only falls back to parsing the legacy backup/container/backup.yaml file if result.Config == nil. As a result, an archive can carry a valid inline config that passes the initial import preflight while also carrying a malformed legacy backup/container/backup.yaml file that is reparsed later from the restored file system.

ParseConfigYamlFile() accepts YAML documents with no container section, and multiple downstream consumers then dereference .Container without checking for nil. Confirmed examples in the instance restore and import flow include backup.UpdateInstanceConfig() and internalImportFromBackup().

An authenticated user with permission to import instance backups may be able to crash the Incus daemon with a crafted backup archive whose inline backup/index.yaml is valid but whose extracted legacy backup.yaml omits container. The crash occurs in the restore path after archive extraction has begun.

The flow is as follows:
A crafted backup archive contains a valid backup/index.yaml file together with a malformed backup/container/backup.yaml file that omits the container section.
backup.GetInfo() parses backup/index.yaml successfully, so bInfo.Config is populated from the inline config.
Because result.Config != nil, GetInfo() does not fall back to backup/container/backup.yaml.
instances_post.go then builds the request from bInfo.Config.Container, which succeeds because the inline config is valid.
Later, storage unpack extracts backup/container/backup.yaml into the instance volume as <mountPath>/backup.yaml.
backend.go then calls backup.UpdateInstanceConfig(..., mountPath), which reparses <mountPath>/backup.yaml through ParseConfigYamlFile().
Because ParseConfigYamlFile() accepts YAML with no container section, backup.Container == nil, and later access to backup.Container.Devices or backup.Container.ExpandedDevices can trigger a nil-pointer dereference.


Affected Files:
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_info.go#L87
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_info.go#L115
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_config_utils.go#L85
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/backup/backup_config_utils.go#L159
 - https://github.com/lxc/incus/blob/v6.22.0/internal/server/storage/backend.go#L809
 - https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/api_internal.go#L749

The initial backup-metadata parser prefers inline backup/index.yaml content:

Affected Code:
```
if hdr.Name == backupIndexPath {
    err = yaml.NewDecoder(tr).Decode(&result)
```

The legacy backup/container/backup.yaml file is only parsed if the inline config is absent:

Affected Code:
```
if result.Config == nil && hdr.Name == "backup/container/backup.yaml" {
    err = yaml.NewDecoder(tr).Decode(&result.Config)
```

ParseConfigYamlFile() accepts an empty YAML document, or one with no container section, without validation:

Affected Code:
```
func ParseConfigYamlFile(path string) (*config.Config, error) {
    data, err := os.ReadFile(path)
    ...
    backupConf := config.Config{}
    err = yaml.Unmarshal(data, &backupConf)
```

UpdateInstanceConfig() conditionally uses backup.Container at first but later dereferences it unconditionally:

Affected Code:
```
if backup.Container != nil {
    backup.Container.Name = b.Name
    backup.Container.Project = b.Project
}

if updateRootDevicePool(backup.Container.Devices, pool.Name) {
    rootDiskDeviceFound = true
}

if updateRootDevicePool(backup.Container.ExpandedDevices, pool.Name) {
    rootDiskDeviceFound = true
}
```

Another confirmed sink is present in internalImportFromBackup():

Affected Code:
```
if allowNameOverride {
    backupConf.Container.Name = instName
}

if instName != backupConf.Container.Name {
    return fmt.Errorf("Instance name requested %q doesn't match instance name in backup config %q", instName, backupConf.Container.Name)
}
```

This was confirmed as follows:

Command:
```
go test ./test/fuzz -run='TestExtractedBackupYAMLMissingContainerNilDereference' -count=1 -v
```

Output:

```
=== RUN   TestExtractedBackupYAMLMissingContainerNilDereference
=== RUN   TestExtractedBackupYAMLMissingContainerNilDereference/legacy_backup_empty
   extracted_backup_yaml_poc_test.go:70: UpdateInstanceConfig panicked on malformed extracted
       backup.yaml (container is nil): runtime error: invalid memory address or nil pointer
       dereference
=== RUN   TestExtractedBackupYAMLMissingContainerNilDereference/legacy_backup_pool_only
   extracted_backup_yaml_poc_test.go:70: UpdateInstanceConfig panicked on malformed extracted
       backup.yaml (container is nil): runtime error: invalid memory address or nil pointer
       dereference
=== RUN   TestExtractedBackupYAMLMissingContainerNilDereference/legacy_backup_volume_only
   extracted_backup_yaml_poc_test.go:70: UpdateInstanceConfig panicked on malformed extracted
       backup.yaml (container is nil): runtime error: invalid memory address or nil pointer
       dereference
--- FAIL: TestExtractedBackupYAMLMissingContainerNilDereference (0.21s)
FAIL
```

It is recommended to validate the parsed legacy backup.yaml structure before any dereference and to fail with a standard error if Container is missing:

Proposed Fix:
```
if backup.Container == nil {
    return errors.New("No container struct in the backup file found")
}
```

That validation should be added at minimum in: backup.UpdateInstanceConfig() and internalImportFromBackup() before any backupConf.Container.* access

More broadly, it is recommended to centralize backup-config validation so that both inline backup/index.yaml and extracted legacy backup.yaml files are checked against the same structural requirements before any restore or import consumer uses them.

A patch is available at https://github.com/lxc/incus/releases/tag/v7.0.0.

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-x5r6-jr56-89pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41684
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v7.0.0
