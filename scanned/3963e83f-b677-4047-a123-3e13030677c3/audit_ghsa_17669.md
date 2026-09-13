# [H] sentry-android unmasked sensitive data in Android Session Replays for users of Jetpack Compose 1.8+

## Summary
Severity: High
Advisory: GHSA-7cjh-xx4r-qh3f
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-7cjh-xx4r-qh3f
Type: github-advisory

## Affected
- Maven: `io.sentry:sentry-android` — affected >=0 <8.14.0
- Maven: `io.sentry:sentry-android-replay` — affected >=0 <8.14.0

## Details
### Impact

Under specific circumstances, text composables may contain unmasked sensitive data in Android session replays.  You may be impacted if you meet the following conditions:
- Using any `sentry-android` with versions < 8.14.0 
- Using Jetpack Compose >= [1.8.0-alpha08](https://developer.android.com/jetpack/androidx/releases/compose-ui#1.8.0-alpha08)
  - This includes any alpha, beta, release candidate, or general availability after this version
- Have configured Sentry Session Replays for Android

> [!IMPORTANT] 
> If you do not use Jetpack Compose or have never used a version >= 1.8.0-alpha08 you are not impacted. 

> [!IMPORTANT] 
> If you have not configured [Session Replays for Mobile](https://docs.sentry.io/product/explore/session-replay/mobile/) you are not impacted.

### How do I check if I'm impacted?

If you meet the conditions above, the `sentry-android` package includes a [specific error log](https://github.com/getsentry/sentry-java/blob/b2920907e6afb69a8027cedb251dd94a3514f0e6/sentry-android-replay/src/main/java/io/sentry/android/replay/viewhierarchy/ComposeViewHierarchyNode.kt#L252-L261) that would indicate you may be impacted. Customers may use [logcat](https://developer.android.com/tools/logcat) to search for this event.

### I'm impacted and want this data deleted

If you've confirmed that you're affected and unmasked sensitive data in Session Replays have reached Sentry servers, you can please see this documentation on [deleting individual replays](https://docs.sentry.io/product/explore/session-replay/web/replay-details/#delete-replays). If you'd like to request bulk deletion, please reach out to your Account Manager or support@sentry.io to request deletion. 

### Patches

Upgrade the `sentry-android` SDK to version [8.14.0](https://github.com/getsentry/sentry-java/releases/tag/8.14.0)

### Workarounds

We recommend upgrading to the latest version of the SDK, but if it is not an option, customers may either:
- Downgrade their use of Jetpack Compose to <= 1.7.x
- Drop session sample rates to 0.0 
```
options.sessionReplay.onErrorSampleRate = 0.0
options.sessionReplay.sessionSampleRate = 0.0
```
Please see our documentation for more information configuring [Session Replays for Android](https://docs.sentry.io/platforms/android/session-replay/#set-up).

### References

This issue was identified in Issue https://github.com/getsentry/sentry-java/issues/4467 and fixed in https://github.com/getsentry/sentry-java/pull/4485

## References
- https://github.com/getsentry/sentry-java/security/advisories/GHSA-7cjh-xx4r-qh3f
- https://github.com/getsentry/sentry-java/issues/4467
- https://github.com/getsentry/sentry-java/pull/4485
- https://github.com/getsentry/sentry-java/commit/8bfa9cceab402e58f6723a0694158d27e8a41a56
- https://github.com/getsentry/sentry-java
- https://github.com/getsentry/sentry-java/releases/tag/8.14.0
