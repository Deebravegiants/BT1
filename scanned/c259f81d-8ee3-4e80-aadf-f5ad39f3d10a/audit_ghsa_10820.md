# [M] Tillitis TKey Client has an Error in Protocol Implementation

## Summary
Severity: Medium
Advisory: GHSA-4w7r-3222-8h6v
CVE: CVE-2026-32953
CWE: CWE-303
Ecosystem: Go
CVSS: CVSS:4.0/AV:P/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-4w7r-3222-8h6v
Type: github-advisory

## Affected
- Go: `github.com/tillitis/tkeyclient` — affected >=0 <1.3.0

## Details
## Impact

Some specific (1 out of 256) User Supplied Secrets (USS) were not used,
making the resulting Compound Device Identifier (CDI) the same as if no
USS was provided.

Affected client applications: all client apps using the
[tkeyclient](https://github.com/tillitis/tkeyclient) Go module.

## Patches

Upgrade to v1.3.0.

**NOTE WELL**: For the affected end users upgrading an app containing
`tkeyclient` to v1.3.0 means their key material will change. An end
user can get their old keys by not entering any USS. Please make sure
to communicate this to end users.

## Affected users

The steps required to assess whether your USS is vulnerable may vary
depending on the client application. The example below shows how to
perform the check using `tkey-ssh-agent` and the known vulnerable USS
`adl`.

1. Insert the TKey into the client
2. Run `tkey-ssh-agent -p --uss`
3. When prompted for a User Supplied Secret, enter `adl`
4. Note the public key and call it `pubkey-with-uss`
5. Remove the TKey from the client
6. Insert the TKey into the client again
7. Run `tkey-ssh-agent -p`
8. Note the public key and call it `pubkey-without-uss`

Expected behavior:
`pubkey-with-uss` and `pubkey-without-uss` should not be equal.

Observed behavior:
`pubkey-with-uss` and `pubkey-without-uss` are equal.

## Workaround

We recommend everyone using `tkeyclient` to update to v1.3.0 and
release new versions of the client apps using it.

However, end users that are unable to upgrade to a new version of a client
app, the recommendation is to change to an unaffected USS. Include
specific instructions for your client app.

## Details

When loading the device app an optional 32 bytes USS digest is also
sent. The intention is to ask the end user to enter a USS of arbitrary
length, hash it, and then send a 32 bytes digest to TKey.

However, there was a bug when sending the digest from the client. The
index in the outgoing buffer is wrong and overwrites the boolean
defining if the USS is used or not.

This means that if the USS digest begins with a 0, the rest of the
digest is not used at all. If it begins with something else, setting
the boolean to true, the USS is used.

The exported `LoadApp()` function calls an internal helper function
`loadApp()` which contains this code:

```go
  if len(secretPhrase) == 0 {
    tx[6] = 0
  } else {
    tx[6] = 1 // Note the 6 here
    // Hash user's phrase as USS
    uss := blake2s.Sum256(secretPhrase)
    copy(tx[6:], uss[:]) // Note that 6 is used again
  }
```

A side effect of this behavior is that only 31 bytes of the USS are
used. This is not considered a security issue, but an option has been
added to enforce use of the full USS. See the release notes for
details. To avoid forcing all users to roll their keys, this option is
disabled by default and must be explicitly enabled.

### The fix

The fix focuses on solving the vulnerability only by: 1) use correct
index, 2) always use the last 31 bytes of the USS:

```go
  if len(secretPhrase) == 0 {
    tx[6] = 0
  } else {
    tx[6] = 1
    // Hash user's phrase as USS
    uss := blake2s.Sum256(secretPhrase)
    copy(tx[7:], uss[1:])
  }
```

This change means the key material of affected end users will change
compared to earlier versions of `tkeyclient`. They have the choice of:

1. Not using a USS and keep their keys.
2. Keep using their USS and use new generated keys.
3. Use another USS and thus new keys.

## References
- https://github.com/tillitis/tkeyclient/security/advisories/GHSA-4w7r-3222-8h6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-32953
- https://github.com/tillitis/tkeyclient/commit/4954dccf0287657edf8d405057e134cdff9c59e8
- https://github.com/tillitis/tkeyclient
- https://github.com/tillitis/tkeyclient/releases/tag/v1.3.0
