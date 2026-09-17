# [M] Lemmy user purging users or communities or banning users can delete images they didn't upload/exclusively use

## Summary
Severity: Medium
Advisory: GHSA-wr2m-38xh-rpc9
CWE: CWE-708
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-wr2m-38xh-rpc9
Type: github-advisory

## Affected
- crates.io: `lemmy_server` — affected >=0.17.0 <0.19.11

## Details
### Summary
An improper uploaded media ownership check can result in inadvertent deletion of media when a user is banned with content removal or purged. This can lead to deletion of media that was not uploaded by the banned/purged user. This also applies to purged communities, in which case all media posted in that community will get deleted without proper ownership check.
This is limited to media with an `image/*` content-type returned by pict-rs.

### Details
Lemmy did not associate users with media uploads until version 0.19.0 ([#3927](https://github.com/LemmyNet/lemmy/pull/3927)).
Back when the first parts of content purging were implemented for 0.17.0 ([#1809](https://github.com/LemmyNet/lemmy/pull/1809)), it was therefore not possible to properly identify media belonging to a specific user for situations in which this data should get erased from pict-rs, Lemmy's media storage backend.

Pict-rs deduplicates uploaded files transparently. As a result, it has two types of media deletion. A regular deletion will only remove the referenced alias, and if there are not other aliases pointing to the same file, the backing file will also be deleted. A purge on the other hand will delete all aliases pointing to the specified file, as well as the file itself.

The logic implemented in 0.17.0 iterated over media URLs related to users and communities when purging them and purged them from pict-rs. This results in a full deletion of the backing media, even if either the same URL was the result of an upload by a different user, or the same media being uploaded by another user with a different alias.
For user purges, Lemmy iterated over all posts they created and applied this to all media referenced in post URLs and post thumbnails. For community purges, this applied to all posts within this community.

Additionally, the deletion of user avatars, banners, as well as the media from all their posts was implemented when users were banned with content removal. This includes local bans and also bans received via federation, when a user gets banned on their home instance.

The function for purging images from pict-rs performs a check at the start to verify that the media `Content-Type` header returned by pict-rs starts with `image/`, which limits this to not affect other media types supported by Lemmy and pict-rs, such as videos.

### Impact

#### Instances with open federation
The vast majority of Lemmy instances has open federation, which means that this can be exploited remotely without any authentication.

#### Instances with limited or no federation
Exploitation requires user interaction by an admin of the targeted instance or a federation-linked instance if federation is enabled.
It may also require authentication, as instances may not have open registrations.

## References
- https://github.com/LemmyNet/lemmy/security/advisories/GHSA-wr2m-38xh-rpc9
- https://github.com/LemmyNet/lemmy/pull/1809
- https://github.com/LemmyNet/lemmy/pull/3927
- https://github.com/LemmyNet/lemmy/pull/5566
- https://github.com/LemmyNet/lemmy
