# [M] ActiveStorage Disk Service Path Traversal via Custom Blob Key Injection

## Summary
Severity: Medium (CVSS 6.5)
Program: Ruby on Rails
Weakness: Path Traversal
Reporter: ksw9722
State: resolved
Disclosed: 2026-05-07T14:04:44.714Z
Source: https://hackerone.com/reports/3580511

## Details
# ActiveStorage Disk Service Path Traversal via Custom Blob Key Injection

## Summary

ActiveStorage's `DiskService#path_for` does not validate or sanitize blob keys before constructing file paths. Combined with the Hash attachable interface — which passes user-supplied `key:` values directly to `Blob.build_after_unfurling` without filtering — an attacker who can influence the Hash passed to `.attach()` can achieve **arbitrary file write, read, and delete** on the server's filesystem.

The `key:` parameter is a [documented feature](https://guides.rubyonrails.org/active_storage_overview.html#attaching-file-io-objects) intended for S3 folder organization, making it likely that developers will incorporate user input into key construction.

**Severity**: High (CVSS 8.1 estimated — depends on application-level exposure)
**Affected component**: `activestorage` (DiskService)
**Affected versions**: All current Rails versions using ActiveStorage with DiskService

---

## Vulnerability Details

### 1. Hash Attachable Splats All Keys Without Filtering

`activestorage/lib/active_storage/attached/changes/create_one.rb:82-88`:

```ruby
when Hash
  ActiveStorage::Blob.build_after_unfurling(
    **attachable.reverse_merge(
      record: record,
      service_name: attachment_service_name
    ).symbolize_keys
  )
```

When a Hash is passed to `.attach()`, **every key-value pair** — including `key:` — is forwarded to `Blob.build_after_unfurling` via `**` splat.

### 2. `build_after_unfurling` Accepts and Stores Arbitrary Keys

`activestorage/app/models/active_storage/blob.rb:86-89`:

```ruby
def build_after_unfurling(key: nil, io:, filename:, content_type: nil, metadata: nil, service_name: nil, identify: true, record: nil)
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3580511_
