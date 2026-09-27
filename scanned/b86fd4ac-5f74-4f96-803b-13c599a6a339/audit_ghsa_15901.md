# [H] Livewire Remote Code Execution on File Uploads

## Summary
Severity: High
Advisory: GHSA-f3cx-396f-7jqp
CVE: CVE-2024-47823
CWE: CWE-20, CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-f3cx-396f-7jqp
Type: github-advisory

## Affected
- Packagist: `livewire/livewire` — affected >=3.0.0-beta.1 <3.5.2
- Packagist: `livewire/livewire` — affected >=0 <2.12.7

## Details
In livewire/livewire prior to `v2.12.7` and `v3.5.2`, the file extension of an uploaded file is guessed based on the MIME type. As a result, the actual file extension from the file name is not validated. An attacker can therefore bypass the validation by uploading a file with a valid MIME type (e.g., `image/png`) and a “.php” file extension.
If the following criteria are met, the attacker can carry out an RCE attack:

- Filename is composed of the original file name using `$file->getClientOriginalName()`
- Files stored directly on your server in a public storage disk
- Webserver is configured to execute “.php” files

### PoC
In the following scenario, an attacker could upload a file called `shell.php` with an `image/png` MIME type and execute it on the remote server.
```php
class SomeComponent extends Component
{
    use WithFileUploads;

    #[Validate('image|extensions:png')]
    public $file;

    public function save()
    {
        $this->validate();

        $this->file->storeAs(
            path: 'images',
            name: $this->file->getClientOriginalName(),
            options: ['disk' => 'public'],
        );
    }
}
```

## References
- https://github.com/livewire/livewire/security/advisories/GHSA-f3cx-396f-7jqp
- https://nvd.nist.gov/vuln/detail/CVE-2024-47823
- https://github.com/livewire/livewire/pull/8624
- https://github.com/livewire/livewire/commit/70503b79f5db75a1eac9bf55826038a6ee5a16d5
- https://github.com/livewire/livewire/commit/cd168c6212ea13d13b82b3132485741f82d9fad9
- https://github.com/livewire/livewire
