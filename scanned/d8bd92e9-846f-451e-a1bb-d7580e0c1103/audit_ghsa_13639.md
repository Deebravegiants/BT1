# [M] Bunkum tokens cached in the AuthenticationService are susceptible to a use-after-free

## Summary
Severity: Medium
Advisory: GHSA-jrf2-h5j6-3rrq
CVE: CVE-2023-45814
CWE: CWE-772
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-jrf2-h5j6-3rrq
Type: github-advisory

## Affected
- NuGet: `Bunkum` — affected >=4.0.0 <4.2.1

## Details
### Impact
First, a little bit of background. So, in the beginning, Bunkum's `AuthenticationService` only supported injecting `IUser`s. However, as Refresh and SoundShapesServer implemented permissions systems support for injecting `IToken`s into endpoints was added. All was well until 4.0.

Bunkum 4.0 then changed to enforce relations between `IToken`s and `IUser`s. This wasn't implemented in a very good way in the `AuthenticationService`, and ended up breaking caching in such a way that cached tokens would persist after the lifetime of the request - since we tried to cache both tokens and users. From that point until now, from what I understand, Bunkum was attempting to use that cached token at the start of the next request once cached.

Naturally, when that token expired, downstream projects like Refresh would remove the object from Realm - and cause the object in the cache to be in a detached state, causing an exception from invalid use of `IToken.User`. So in other words, a use-after-free since Realm can't manage the lifetime of the cached token.

Security-wise, the scope is fairly limited, can only be pulled off on a couple endpoints given a few conditions, and you can't guarantee which token you're going to get. Also, the token *would* get invalidated properly if the endpoint had either a `IToken` usage or a `IUser` usage. User interaction is required as authenticated requests must be performed.

### Patches
The fix is to just wipe the token cache after the request was handled, which is now in `4.2.1`. I'd recommend that you update. Unfortunately, there are no real workarounds for other versions in the 4.X.X range.

## References
- https://github.com/LittleBigRefresh/Bunkum/security/advisories/GHSA-jrf2-h5j6-3rrq
- https://nvd.nist.gov/vuln/detail/CVE-2023-45814
- https://github.com/LittleBigRefresh/Bunkum/commit/6e109464ed9255f558182f001f475a378405ff76
- https://github.com/LittleBigRefresh/Bunkum
