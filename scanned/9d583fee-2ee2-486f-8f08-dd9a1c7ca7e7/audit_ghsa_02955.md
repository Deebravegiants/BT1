# [H] Missing Authorization with Default Settings in Dashboard UI

## Summary
Severity: High
Advisory: GHSA-7rq6-7gv8-c37h
CVE: CVE-2021-41238
CWE: CWE-862
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-7rq6-7gv8-c37h
Type: github-advisory

## Affected
- NuGet: `Hangfire.Core` — affected >=1.7.25 <1.7.26

## Details
Dashboard UI in Hangfire.Core uses authorization filters to protect it from showing sensitive data to unauthorized users. By default when no custom authorization filters specified, `LocalRequestsOnlyAuthorizationFilter` filter is being used to allow only local requests and prohibit all the remote requests to provide sensible, protected by default settings.

However due to the recent changes, in version 1.7.25 no authorization filters are used by default, allowing remote requests to succeed.

### Impact

Missing authorization when default options are used for the Dashboard UI, e.g. when no custom authorization rules are used as recommended in the [Using Dashboard](https://docs.hangfire.io/en/latest/configuration/using-dashboard.html#configuring-authorization) documentation article. 

#### Impacted

If you are using `UseHangfireDashboard` method with default `DashboardOptions.Authorization` property value, then your installation is impacted:

```csharp
app.UseHangfireDashboard(); // Impacted
app.UseHangfireDashboard("/hangfire", new DashboardOptions()); // Impacted
```

#### Not Impacted

If any other authorization filter is specified in the `DashboardOptions.Authorization` property, the you are not impacted:

```csharp
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new []{ new SomeAuthorizationFilter(); } // Not impacted
});
```

### Patches

Patch is already available in version [1.7.26](https://github.com/HangfireIO/Hangfire/releases/tag/v1.7.26) and already available on NuGet.org, please see [Hangfire.Core 1.7.26](https://www.nuget.org/packages/Hangfire.Core/1.7.26). Default authorization rules now prohibit remote requests by default again by including the `LocalRequestsOnlyAuthorizationFilter` filter to the default settings. Please upgrade to the newest version in order to mitigate the issue.

### Workarounds

It is possible to fix the issue by using the `LocalRequestsOnlyAuthorizationFilter` explicitly when configuring the Dashboard UI. In this case upgrade is not required.

```csharp
// using Hangfire.Dashboard;

app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new []{ new LocalRequestsOnlyAuthorizationFilter(); }
});
```

### References

Original GitHub Issue: https://github.com/HangfireIO/Hangfire/issues/1958

## References
- https://github.com/HangfireIO/Hangfire/security/advisories/GHSA-7rq6-7gv8-c37h
- https://nvd.nist.gov/vuln/detail/CVE-2021-41238
- https://github.com/HangfireIO/Hangfire/issues/1958
- https://github.com/HangfireIO/Hangfire
- https://www.nuget.org/packages/Hangfire.Core
