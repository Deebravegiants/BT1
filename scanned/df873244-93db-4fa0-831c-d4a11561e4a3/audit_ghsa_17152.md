# [M] Serverpod improved security for stored password hashes

## Summary
Severity: Medium
Advisory: GHSA-r75m-26cq-mjxc
CVE: CVE-2024-29886
CWE: CWE-916
Ecosystem: Pub
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-03-28
Source: https://github.com/advisories/GHSA-r75m-26cq-mjxc
Type: github-advisory

## Affected
- Pub: `serverpod_auth_server` — affected >=0 <1.2.6

## Details
## Description

### Improved security for stored password hashes
Serverpod now uses the OWASP, [source](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html#introduction), recommended Argon2Id password hash algorithm to store password hashes for the email authentication module.

Starting from Serverpod `1.2.6` all users that either creates an account or authenticates with the server will have their password stored using the safer algorithm. No changes are required from the developer to start storing passwords using the safer algorithm.

### Why did we change how passwords are stored?
An issue was identified with the old password hash algorithm that made it susceptible to rainbow attacks if the database was compromised.

It is strongly recommended to migrate your existing password hashes.

### Migrate existing password hashes
The email authentication module provides a helper method to migrate all the existing legacy password hashes in the database. Simply call  `Emails.migrateLegacyPasswordHashes(...)` with a session instance as an argument to migrate the password hashes.

The method is implemented as an idempotent operation and will yield the same result regardless of how many times it is called.

We recommend either implementing a web server route that can be called remotely or by calling the method as part of starting the server.

Following is example code for implementing a web server route.

<details><summary><h4>Web server route code</h4></summary>

```dart
import 'dart:io';

import 'package:serverpod/serverpod.dart';
import 'package:serverpod_auth_server/module.dart' as auth;

class MigratePasswordsRoute extends Route {
  @override
  Future<bool> handleCall(Session session, HttpRequest request) async {
    request.response.writeln(
      'Migrating legacy passwords, check the server logs for progress updates.',
    );
    _migratePasswords(session);
    return true;
  }
}

Future<void> _migratePasswords(Session session) async {
  session.log('Starting to migrate passwords.');

  var totalMigratedPasswords = 0;
  while (true) {
    try {
      var entriesMigrated = await auth.Emails.migrateLegacyPasswordHashes(
        session,
        // Process 100 database entries at a time
        batchSize: 100,
        // Stop after 500 entries have been migrated
        maxMigratedEntries: 500,
      );

      totalMigratedPasswords += entriesMigrated;
      session.log(
        'Migrated $entriesMigrated password entries, total $totalMigratedPasswords.',
      );

      if (entriesMigrated == 0) break;

      // Delay to avoid overloading the database
      await Future.delayed(Duration(seconds: 1));
    } catch (e) {
      session.log('Error migrating passwords: $e');
    }
  }

  session.log('Finished migrating passwords.');
}
```

</details>

### How we migrate existing password hashes
Since password hashes can’t be recalculated without knowledge of the plain text password, the method in the email authentication module applies the new algorithm to the already stored password hashes.

When the affected users later authenticate, their password hash will be calculated using both algorithms in tandem. If the authentication is accepted, the stored password hash will be updated to only use the new algorithm so that further authentication only needs to run the new algorithm.

### Impact
All versions of `serverpod_auth_server` pre `1.2.6`

### Patches
Upgrading to version `1.2.6` resolves this issue.

## References
- https://github.com/serverpod/serverpod/security/advisories/GHSA-r75m-26cq-mjxc
- https://nvd.nist.gov/vuln/detail/CVE-2024-29886
- https://github.com/serverpod/serverpod/commit/a78b9e9f1de74d1300633a122b6cc0f064139ad6
- https://github.com/serverpod/serverpod
