# [?] fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-08-03
Source: https://github.com/ZcashFoundation/zebra/commit/dfb284116a50b257bf2656d8ce8a1d0255366ada
Type: security-commit

## Details
fix(inbound): score peers for RouterError from invalid gossiped blocks (GHSA-8hh2-hrf2-cqf4)

Co-Authored-By: Evan Forbes <42654277+evan-forbes@users.noreply.github.com>

During integration with the existing security fixes, retain their
release-note entries and add the invalid gossiped-block scoring
advisory under the shared Security section.

Conflicts:
    CHANGELOG.md
